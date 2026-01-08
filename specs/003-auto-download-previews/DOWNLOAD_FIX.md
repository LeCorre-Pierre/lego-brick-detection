# Image Download Fix - User-Agent Required

## Problem Identified
BrickLink's image server returns **HTTP 403 Forbidden** when requests don't include a User-Agent header, causing all downloads to fail and generate placeholders instead.

## Test Results

### Before Fix
- All requests: HTTP 403
- Images created: 472 bytes (placeholder with text)
- Status: ❌ FAILED

### After Fix  
- All requests: HTTP 200  
- Real image sizes: 22-93 KB (actual brick images)
- Status: ✅ SUCCESS

## Fix Applied
Added User-Agent header to all HTTP requests in `src/utils/image_downloader.py`:

```python
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
headers = {'User-Agent': USER_AGENT}
response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
```

## Verification
Run the command-line test:
```bash
python tests/test_download_cli.py
```

Expected output: ✅ 5/5 tests passed

## Downloaded Images Confirmed
- `3001.png`: 26 KB ✓
- `3003.png`: 35 KB ✓  
- `3005.png`: 23 KB ✓
- `2780.png`: 93 KB ✓

All images are valid PNG files with proper brick imagery from BrickLink.

## Feature Status
✅ **FULLY FUNCTIONAL** - Downloads work correctly with User-Agent header.
