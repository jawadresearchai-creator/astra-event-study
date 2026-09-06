"""Acquire bounded Yahoo chart payloads and preserve exact response bytes.

No credential access. Re-running uses immutable cached payloads unless --refresh
is explicitly supplied. Normalization never fills missing prices.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import importlib.metadata
from zoneinfo import ZoneInfo

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data' / 'processed'
AUDIT = ROOT / 'data' / 'manifest'

def epoch(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp())

def fetch(ticker, interval, start, end, refresh=False):
    folder = RAW / interval
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{ticker}.json'
    metadata_path = folder / f'{ticker}.metadata.json'
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
    params = dict(period1=epoch(start), period2=epoch(end), interval=interval,
                  events='div,splits', includePrePost='false')
    if not path.exists() or refresh:
        response = None
        for attempt in range(2):
            try:
                response = requests.get(url, params=params,
                    headers={'User-Agent': 'AstraEventStudy/1.0 academic-research'}, timeout=35)
                response.raise_for_status()
                payload = response.json()
                if payload.get('chart', {}).get('error'):
                    raise ValueError(str(payload['chart']['error']))
                path.write_bytes(response.content)
                meta = dict(ticker=ticker, interval=interval, source_url=response.url,
                    retrieved_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                    http_status=response.status_code, bytes=len(response.content),
                    sha256=hashlib.sha256(response.content).hexdigest(),
                    source='Yahoo Finance chart API', adjustment='vendor adjusted close',
                    availability='publicly accessible; redistribution rights not assumed')
                metadata_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
                break
            except Exception:
                if attempt: raise
                time.sleep(1)
    blob = path.read_bytes()
    meta = json.loads(metadata_path.read_text(encoding='utf-8'))
    assert hashlib.sha256(blob).hexdigest() == meta['sha256'], 'Raw hash mismatch'
    result = json.loads(blob)['chart']['result'][0]
    timestamps = result.get('timestamp', [])
    if not timestamps: raise ValueError(f'No timestamps for {ticker} {interval}')
    times = pd.to_datetime(timestamps, unit='s', utc=True).tz_convert('America/New_York')
    quote = result['indicators']['quote'][0]
    df = pd.DataFrame(quote)
    df.insert(0, 'Timestamp', times)
    if interval == '1d':
        adjusted = result['indicators'].get('adjclose', [{}])[0].get('adjclose')
        if adjusted is None: raise ValueError(f'Missing adjusted close for {ticker}')
        df['adjusted_close'] = adjusted
        df['Date'] = df['Timestamp'].dt.strftime('%Y-%m-%d')
        assert not df['Date'].duplicated().any(), f'Duplicate date {ticker}'
    df['ticker'] = ticker
    assert (df['close'].dropna() > 0).all(), f'Nonpositive close {ticker}'
    meta.update(rows=len(df), first_timestamp=str(times.min()), last_timestamp=str(times.max()))
    return df, meta

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--intraday', action='store_true')
    args = parser.parse_args()
    for folder in [OUT, AUDIT]: folder.mkdir(parents=True, exist_ok=True)
    sample = pd.read_csv(ROOT / 'config/sample.csv')
    tickers = sample.ticker.tolist() + ['SPY', 'QQQ', 'XLK']
    manifests, failures, frames = [], [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(fetch, ticker, '1d', '2024-09-01', '2026-09-05', args.refresh): ticker
                for ticker in tickers}
        for job in concurrent.futures.as_completed(jobs):
            ticker = jobs[job]
            try:
                df, meta = job.result(); frames.append(df); manifests.append(meta)
                print(f'DAILY {ticker}: {len(df)} rows', flush=True)
            except Exception as exc:
                failures.append(dict(ticker=ticker, interval='1d', error=str(exc)))
                print(f'FAILED {ticker}: {exc}', flush=True)
    if frames:
        long = pd.concat(frames, ignore_index=True)
        long.sort_values(['ticker', 'Date']).to_csv(OUT / 'daily_ohlcv.csv', index=False)
        prices = long.pivot(index='Date', columns='ticker', values='adjusted_close').sort_index()
        prices.to_csv(OUT / 'prices.csv', float_format='%.12g')
        pd.DataFrame([dict(ticker=t, first_valid=str(prices[t].first_valid_index()),
                    last_valid=str(prices[t].last_valid_index()), n=prices[t].count(),
                    event_day_present=pd.notna(prices[t].get('2026-09-03')),
                    day_one_present=pd.notna(prices[t].get('2026-09-04')))
                    for t in prices.columns]).to_csv(OUT / 'coverage.csv', index=False)
    if args.intraday:
        intra = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            jobs = {pool.submit(fetch, t, '5m', '2026-08-24', '2026-09-05', args.refresh): t
                    for t in tickers}
            for job in concurrent.futures.as_completed(jobs):
                t = jobs[job]
                try:
                    df, meta = job.result(); intra.append(df); manifests.append(meta)
                    print(f'INTRADAY {t}: {len(df)} bars (archive only)', flush=True)
                except Exception as exc:
                    failures.append(dict(ticker=t, interval='5m', error=str(exc)))
        if intra: pd.concat(intra, ignore_index=True).to_csv(OUT / 'intraday_archive.csv', index=False)
    versions = {package: importlib.metadata.version(package) for package in
                ['pandas', 'numpy', 'requests']}
    (AUDIT / 'acquisition.json').write_text(json.dumps(dict(
        schema_version=1, study='astra-event-study', cutoff='2026-09-04',
        generated_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        github_sha=os.environ.get('GITHUB_SHA'), github_run_id=os.environ.get('GITHUB_RUN_ID'),
        python=sys.version, platform=platform.platform(), packages=versions,
        sources=sorted(manifests, key=lambda r: (r['interval'],r['ticker'])),
        failures=failures), indent=2), encoding='utf-8')
    if any(x['interval']=='1d' for x in failures):
        raise SystemExit('Daily acquisition incomplete; inspect manifest before estimation')

if __name__ == '__main__': main()
