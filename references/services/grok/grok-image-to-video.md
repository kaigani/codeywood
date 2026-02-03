# Grok Imagine Video

> Generate videos from images with audio using xAI's Grok Imagine Video model. 


## Overview

- **Endpoint**: `https://fal.run/xai/grok-imagine-video/image-to-video`
- **Model ID**: `xai/grok-imagine-video/image-to-video`
- **Category**: image-to-video
- **Kind**: inference
**Tags**: grok, xai, image-to-video, i2v



## API Information

This model can be used via our HTTP API or more conveniently via our client libraries.
See the input and output schema below, as well as the usage examples.


### Input Schema

The API accepts the following input parameters:


- **`prompt`** (`string`, _required_):
  Text description of desired changes or motion in the video.
  - Examples: "Medieval knight in ornate armor walking through a mystical forest, bioluminescent plants pulsing with light, ancient stone ruins overgrown with glowing vines, over-the-shoulder camera, dark fantasy aesthetic, volumetric fog and Lumen lighting"

- **`duration`** (`integer`, _optional_):
  Video duration in seconds. Default value: `6`
  - Default: `6`
  - Range: `1` to `15`

- **`aspect_ratio`** (`AspectRatioEnum`, _optional_):
  Aspect ratio of the generated video. Default value: `"auto"`
  - Default: `"auto"`
  - Options: `"auto"`, `"16:9"`, `"4:3"`, `"3:2"`, `"1:1"`, `"2:3"`, `"3:4"`, `"9:16"`

- **`resolution`** (`ResolutionEnum`, _optional_):
  Resolution of the output video. Default value: `"720p"`
  - Default: `"720p"`
  - Options: `"480p"`, `"720p"`

- **`image_url`** (`string`, _required_):
  URL of the input image for video generation.
  - Examples: "https://v3b.fal.media/files/b/0a8b90e0/BFLE9VDlZqsryU-UA3BoD_image_004.png"



**Required Parameters Example**:

```json
{
  "prompt": "Medieval knight in ornate armor walking through a mystical forest, bioluminescent plants pulsing with light, ancient stone ruins overgrown with glowing vines, over-the-shoulder camera, dark fantasy aesthetic, volumetric fog and Lumen lighting",
  "image_url": "https://v3b.fal.media/files/b/0a8b90e0/BFLE9VDlZqsryU-UA3BoD_image_004.png"
}
```

**Full Example**:

```json
{
  "prompt": "Medieval knight in ornate armor walking through a mystical forest, bioluminescent plants pulsing with light, ancient stone ruins overgrown with glowing vines, over-the-shoulder camera, dark fantasy aesthetic, volumetric fog and Lumen lighting",
  "duration": 6,
  "aspect_ratio": "auto",
  "resolution": "720p",
  "image_url": "https://v3b.fal.media/files/b/0a8b90e0/BFLE9VDlZqsryU-UA3BoD_image_004.png"
}
```


### Output Schema

The API returns the following output format:

- **`video`** (`VideoFile`, _required_):
  The generated video.
  - Examples: {"height":720,"duration":6.041667,"url":"https://v3b.fal.media/files/b/0a8b90e0/0Ci1dviuSnEyUZzBUq-_5_nu7MrAAa.mp4","fps":24,"width":1280,"file_name":"0Ci1dviuSnEyUZzBUq-_5_nu7MrAAa.mp4","num_frames":145,"content_type":"video/mp4"}



**Example Response**:

```json
{
  "video": {
    "height": 720,
    "duration": 6.041667,
    "url": "https://v3b.fal.media/files/b/0a8b90e0/0Ci1dviuSnEyUZzBUq-_5_nu7MrAAa.mp4",
    "fps": 24,
    "width": 1280,
    "file_name": "0Ci1dviuSnEyUZzBUq-_5_nu7MrAAa.mp4",
    "num_frames": 145,
    "content_type": "video/mp4"
  }
}
```


## Usage Examples

### cURL

```bash
curl --request POST \
  --url https://fal.run/xai/grok-imagine-video/image-to-video \
  --header "Authorization: Key $FAL_KEY" \
  --header "Content-Type: application/json" \
  --data '{
     "prompt": "Medieval knight in ornate armor walking through a mystical forest, bioluminescent plants pulsing with light, ancient stone ruins overgrown with glowing vines, over-the-shoulder camera, dark fantasy aesthetic, volumetric fog and Lumen lighting",
     "image_url": "https://v3b.fal.media/files/b/0a8b90e0/BFLE9VDlZqsryU-UA3BoD_image_004.png"
   }'
```

### Python

Ensure you have the Python client installed:

```bash
pip install fal-client
```

Then use the API client to make requests:

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "xai/grok-imagine-video/image-to-video",
    arguments={
        "prompt": "Medieval knight in ornate armor walking through a mystical forest, bioluminescent plants pulsing with light, ancient stone ruins overgrown with glowing vines, over-the-shoulder camera, dark fantasy aesthetic, volumetric fog and Lumen lighting",
        "image_url": "https://v3b.fal.media/files/b/0a8b90e0/BFLE9VDlZqsryU-UA3BoD_image_004.png"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
```

### JavaScript

Ensure you have the JavaScript client installed:

```bash
npm install --save @fal-ai/client
```

Then use the API client to make requests:

```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("xai/grok-imagine-video/image-to-video", {
  input: {
    prompt: "Medieval knight in ornate armor walking through a mystical forest, bioluminescent plants pulsing with light, ancient stone ruins overgrown with glowing vines, over-the-shoulder camera, dark fantasy aesthetic, volumetric fog and Lumen lighting",
    image_url: "https://v3b.fal.media/files/b/0a8b90e0/BFLE9VDlZqsryU-UA3BoD_image_004.png"
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  },
});
console.log(result.data);
console.log(result.requestId);
```


## Additional Resources

### Documentation

- [Model Playground](https://fal.ai/models/xai/grok-imagine-video/image-to-video)
- [API Documentation](https://fal.ai/models/xai/grok-imagine-video/image-to-video/api)
- [OpenAPI Schema](https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=xai/grok-imagine-video/image-to-video)

### fal.ai Platform

- [Platform Documentation](https://docs.fal.ai)
- [Python Client](https://docs.fal.ai/clients/python)
- [JavaScript Client](https://docs.fal.ai/clients/javascript)
