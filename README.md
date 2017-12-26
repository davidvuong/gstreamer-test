# gstreamer-test

https://gstreamer.freedesktop.org/documentation/index.html

## Installation

```bash
docker build . --tag davidvuong/gstreamer-test
```

If you're on a Mac and don't want to do this in Docker:

```bash
brew install gstreamer
brew install gst-plugins-base gst-libav gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-rtsp-server
```

Install `gst-python` for Python bindings:

```bash
brew install gst-python
```

## Running

```bash
docker run --rm -it -v $(pwd):/root/app -w /root/app davidvuong/gstreamer-test bash
```

## Compiling

```bash
# Only gstreamer
gcc Main.c -o app.o `pkg-config --cflags --libs gstreamer-1.0`

# Including gst-rtsp-server
gcc src/gst-rtsp-server-test.c -o rtsp-server.o `pkg-config --cflags --libs gstreamer-1.0 gstreamer-rtsp-server-1.0 gstreamer-rtsp-1.0`
```

## Building a RTSP Server

You can use `gst-rtsp-server` (https://github.com/GStreamer/gst-rtsp-server) which is a library built on top of gstreamer to build an RTSP server. You can read their docs here (https://github.com/GStreamer/gst-rtsp-server/tree/master/docs).

## Ramblings

Listen to an MJPEG stream, wrap it up into a mkv container and store it in a file:

```bash
gst-launch-1.0 -v souphttpsrc location=http://127.0.0.1:9191/stream do-timestamp=true ! multipartdemux ! image/jpeg,width=640,height=480 ! matroskamux ! filesink location=mjpeg.mkv
```

Play random video from `videotestsrc`:

```
gst-launch-1.0 -v videotestsrc ! video/x-raw,width=1280,height=720 ! autovideosink
```
