#!/usr/bin/env python3
import os
import cv2
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

from gi.repository import Gst, GstRtspServer, GObject
from nn_engine import Engine
import vms

class SensorFactory(GstRtspServer.RTSPMediaFactory):
    """MediaFactory for parsing data from an RTSP via cv2.VideoCapture.

    The original source accepts input from a webcam (cv2.VideoCapture(0)) and passes the buffer
    directly to `gst`. Our implementation does a bit more. It reads the source from an RTSP stream, pulls
    out frames and passes them into a CNN (defined by `engine`). The results the CNN are then passed
    to the gst-rtsp-server.

    see: https://stackoverflow.com/questions/47396372/write-opencv-frames-into-gstreamer-rtsp-server-pipeline?rq=1

    """
    def __init__(self, rtsp_url, engine, **properties):
        super(SensorFactory, self).__init__(**properties)

        self.engine = engine
        self.video_capture = cv2.VideoCapture(rtsp_url)
        self.video_capture.read()

        self.number_frames = 0
        self.launch_string = ' ! '.join([
            'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME caps=video/x-raw,format=BGR,width=1280,height=720',
            'videoconvert ! video/x-raw,format=I420',
            'x264enc',
            'rtph264pay config-interval=1 name=pay0 pt=96',
        ])

    def on_need_data(self, src, length):
        ret, frame = self.video_capture.read()
        self.number_frames += 1
        if not ret:
            return None

        if (self.number_frames % 15) == 0:
            result = self.engine.predict_bytes(cv2.imencode('.jpg', frame)[1].tobytes())
            text = '%s: %0.3f' % (result[0]['class'], result[0]['confidence'])
            frame = cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

        fps = 30
        duration = 1 / fps * Gst.SECOND  # duration of a frame in nanoseconds

        data = frame.tostring()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        buf.duration = duration

        timestamp = self.number_frames * duration
        buf.pts = int(timestamp)
        buf.dts = int(timestamp)
        buf.offset = timestamp

        self.number_frames += 1
        push_buffer_response = src.emit('push-buffer', buf)
        print('pushed buffer, frame {}, duration {}ns, durations {}s'.format(
            self.number_frames,
            duration,
            duration / Gst.SECOND)
        )
        if push_buffer_response != Gst.FlowReturn.OK:
            print(push_buffer_response)

    def do_create_element(self, url):
        """Construct and return a Gst.Element that is a Gst.Bin containing the elements to use for streaming the media.

        The bin should contain payloaders pay\%d for each stream. The default implementation of this function
        returns the bin created from the launch parameter.

        see: https://lazka.github.io/pgi-docs/GstRtspServer-1.0/classes/RTSPMediaFactory.html#GstRtspServer.RTSPMediaFactory.do_configure
        """
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        # GstAppSrc — Easy way for applications to inject buffers into a pipeline
        #
        # see: https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-libs/html/gst-plugins-base-libs-appsrc.html
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)


class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, **properties):
        super(GstServer, self).__init__(**properties)

        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        vms_client = vms.VMS(
            'http',
            os.environ['VMS)HOST'],
            os.environ['VMS_PORT'],
            os.environ['VMS_USERNAME'],
            os.environ['VMS_PASSWORD'],
        )
        camera = vms_client.get_cameras()[0]
        rtsp_url = camera['rtsp_url']

        engine = Engine('.../path/to/model')

        self.factory = SensorFactory(rtsp_url, engine)
        self.factory.set_shared(True)
        self.get_mount_points().add_factory('/live', self.factory)
        self.attach(None)

        print('rtsp-server started and ready to accept connections')


GObject.threads_init()
Gst.init(None)

server = GstServer()

loop = GObject.MainLoop()
loop.run()
