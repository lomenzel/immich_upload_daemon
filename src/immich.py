import aiohttp
import aiofiles
import os

from datetime import datetime
from loguru import logger

async def upload(base_url: str, api_key: str, file: str) -> bool:
    stats = os.stat(file)

    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key,
    }

    # Convert timestamps to ISO format for JSON compatibility.
    data = {
        'deviceAssetId': f'{file}-{stats.st_mtime}',
        'deviceId': 'python',
        'fileCreatedAt': datetime.fromtimestamp(stats.st_mtime).isoformat(),
        'fileModifiedAt': datetime.fromtimestamp(stats.st_mtime).isoformat(),
        'isFavorite': 'false',
    }

    async with aiohttp.ClientSession() as session:
        # Build the form-data for upload.
        form = aiohttp.FormData()
        for key, value in data.items():
            form.add_field(key, value)
        
        async with aiofiles.open(file, 'rb') as f:
            file_data = await f.read()
            form.add_field('assetData',
                           file_data,
                           filename=os.path.basename(file),
                           content_type='application/octet-stream')

        async with session.post(f'{base_url}/assets', headers=headers, data=form) as response:
            response_json = await response.json()
            status = response_json.get('status')
            if status == 'created':
                logger.success(f'{file} uploaded successfully')
                return True
            elif status == 'duplicate':
                logger.warning(f'{file} already uploaded')
                return True
            logger.error(f'Failed to upload {file}: {response_json}')
            return False
