# gstreamer-test

https://gstreamer.freedesktop.org/documentation/index.html

## Installation

```bash
docker build . --tag davidvuong/gstreamer-test
```

If you're on a Mac and don't want to do this in Docker:

```bash
brew install x264
brew install gstreamer
brew install gst-plugins-base gst-libav gst-plugins-good gst-plugins-bad gst-rtsp-server
brew install gst-plugins-ugly --with-x264
```

Install `gst-python` for Python bindings:

```bash
brew install gst-python
```

For Python3 support run with `--with-python3`:

```bash
brew install gst-python --without-python --with-python3
```

If you don't have `--without-python`, you'll get an error (only supports either py2 or py3):

```
Error: Options --with-python and --with-python3 are mutually exclusive.
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

You can enable logging by setting the `GST_DEBUG` environment var (see: https://gstreamer.freedesktop.org/documentation/tutorials/basic/debugging-tools.html). For example:

```bash
GST_DEBUG=2 ./rtsp-server.o
```

**NOTE:** gst-rtsp-server kind of requires you need `GST_DEBUG=2` to be set so you can see runtime errors. If you have an error in your pipeline for e.g. without this environment variable, you will not know what went wrong. For example:

```
0:00:10.794030000 21756 0x7ff6cd81d940 ERROR           GST_PIPELINE grammar.y:740:gint gst_parse_perform_link(link_t *, graph_t *): could not link videotestsrc0 to pay0
0:00:10.794078000 21756 0x7ff6cd81d940 WARN        rtspmediafactory rtsp-media-factory.c:1427:default_create_element: recoverable parsing error: could not link videotestsrc0 to pay0
0:00:10.804737000 21756 0x7ff6cc0390a0 WARN                 basesrc gstbasesrc.c:2939:void gst_base_src_loop(GstPad *):<videotestsrc0> error: Internal data stream error.
0:00:10.804762000 21756 0x7ff6cc0390a0 WARN                 basesrc gstbasesrc.c:2939:void gst_base_src_loop(GstPad *):<videotestsrc0> error: streaming stopped, reason not-linked (-1)
0:00:10.804861000 21756 0x7ff6cd816800 WARN               rtspmedia rtsp-media.c:2439:default_handle_message: 0x7ff6cd83c180: got error Internal data stream error. (gstbasesrc.c(2939): void gst_base_src_loop(GstPad *) (): /GstPipeline:media-pipeline/GstBin:bin0/GstVideoTestSrc:videotestsrc0:
```

This was the error I got when trying to play video after connecting to the RTSP stream.
