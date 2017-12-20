# gstreamer-test

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
brew install gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-rtsp-server
```
