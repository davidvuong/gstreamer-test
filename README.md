# gstreamer-test

https://gstreamer.freedesktop.org/documentation/index.html

## Installation

```bash
docker build . --tag davidvuong/gstreamer-test
```

## Running

```bash
docker run --rm -it -v $(pwd):/root/app -w /root/app davidvuong/gstreamer-test bash
```

## Compiling

```bash
gcc Main.c -o app `pkg-config --cflags --libs gstreamer-1.0`
```

## Mac OSX

```bash
brew install gstreamer
brew install gst-plugins-base gst-libav gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-rtsp-server
```

Install `gst-python` for Python bindings:

```bash
brew install gst-python
```

## Ramblings

Listen to an MJPEG stream, wrap it up into a mkv container and store it in a file:

```bash
gst-launch-1.0 -v souphttpsrc location=http://127.0.0.1:9191/stream do-timestamp=true ! multipartdemux ! image/jpeg,width=640,height=480 ! matroskamux ! filesink location=mjpeg.mkv
```
