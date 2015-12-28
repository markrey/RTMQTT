////////////////////////////////////////////////////////////////////////////
//
//  This file is part of RTMQTT
//
//  Copyright (c) 2015, richards-tech, LLC
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to use,
//  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
//  Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
//  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
//  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#include <Python.h>
#include "RTUVCCamGlue.h"
#include <pthread.h>
#include <termios.h>
#include <unistd.h>
#include <signal.h>
#include <sys/ioctl.h>

static pthread_t rtPyThread;
static RTUVCCamGlue rtPyGlue;
static int argc;
static char **argv;
static bool showWindow;

void *runThread(void *)
{
    rtPyGlue.startLib(argc, argv, showWindow);
    pthread_exit(0);
}

static PyObject *start(PyObject *self, PyObject *args)
{
    PyObject *cmdArgs;

    if (!PyArg_ParseTuple(args, "O!i", &PyList_Type, &cmdArgs, &showWindow)) {
        printf("Bad argument to start\n");
        Py_RETURN_NONE;
    }

    argc = PyList_Size(cmdArgs);
    argv = (char **)malloc(argc * sizeof(char *));

    for (int i = 0; i < argc; i++) {
        char *arg = PyString_AsString(PyList_GetItem(cmdArgs, i));
        argv[i] = (char *)malloc(strlen(arg) + 1);
        strcpy(argv[i], arg);
    }

    pthread_create(&rtPyThread, NULL, runThread, NULL);

    Py_RETURN_NONE;
}

static PyObject *stop(PyObject *self, PyObject *args)
{
    void *threadRes;
    rtPyGlue.stopLib();
    pthread_join(rtPyThread, &threadRes);
    Py_RETURN_NONE;
}

static PyObject *checkDaemonMode(PyObject *self, PyObject *args)
{
    bool mode = rtPyGlue.checkDaemonMode();

    return Py_BuildValue("i", mode);
}
static PyObject *setWindowTitle(PyObject *self, PyObject *args)
{
    char *title;

    if (!PyArg_ParseTuple(args, "s", &title)) {
        printf("Bad argument to setWindowTitle\n");
        Py_RETURN_NONE;
    }

    rtPyGlue.setWindowTitle(title);
    Py_RETURN_NONE;
}

static PyObject *displayImage(PyObject *self, PyObject *args)
{
    unsigned char *image;
    int length;
    int width;
    int height;
    char *timestamp;

    if (!PyArg_ParseTuple(args, "s#iis", &image, &length, &width, &height, &timestamp)) {
        printf("Bad argument to displayImage\n");
        Py_RETURN_NONE;
    }

    rtPyGlue.displayImage(image, length, width, height, timestamp);
    Py_RETURN_NONE;
}

static PyObject *displayJpegImage(PyObject *self, PyObject *args)
{
    unsigned char *image;
    int length;
    char *timestamp;

    if (!PyArg_ParseTuple(args, "s#s", &image, &length, &timestamp)) {
        printf("Bad argument to displayJpegImage\n");
        Py_RETURN_NONE;
    }

    rtPyGlue.displayJpegImage(image, length, timestamp);
    Py_RETURN_NONE;
}

static PyObject *vidCapOpen(PyObject *self, PyObject *args)
{
    int cameraNum;
    int width;
    int height;
    int rate;

    if (!PyArg_ParseTuple(args, "iiii", &cameraNum, &width, &height, &rate)) {
        printf("Bad argument to vidCapOpen\n");
        return Py_BuildValue("i", 0);
    }

    return Py_BuildValue("i", rtPyGlue.vidCapOpen(cameraNum, width, height, rate));
}

static PyObject *vidCapClose(PyObject *self, PyObject *args)
{
    int cameraNum;

    if (!PyArg_ParseTuple(args, "i", &cameraNum)) {
        printf("Bad argument to vidCapClose\n");
        return Py_BuildValue("i", 0);
    }

    return Py_BuildValue("i", rtPyGlue.vidCapClose(cameraNum));
}

static PyObject *vidCapGetFrame(PyObject *self, PyObject *args)
{
    int cameraNum;
    int width = 0;
    int height = 0;
    int rate = 0;
    bool jpeg = false;
    unsigned char *frame = NULL;
    int length = 0;

    if (!PyArg_ParseTuple(args, "i", &cameraNum)) {
        printf("Bad argument to getAVData\n");
        return Py_BuildValue("is#iiii", false, frame, length,
                             jpeg, width, height, rate);
    }
    bool ret = rtPyGlue.vidCapGetFrame(cameraNum, &frame, length, jpeg, width, height, rate);
    PyObject* retData = Py_BuildValue("is#iiii", ret, frame, length,
                                      jpeg, width, height, rate);
    if (frame != NULL)
        free(frame);
    return retData;
}

static PyMethodDef RTUVCCamMethods[] = {
    {"start", (PyCFunction)start, METH_VARARGS,
    "Starts the RTUVCCam library.\n"
    "Call this before calling any other RTUVCCam functions.\n"
    "The function takes three parameters:\n"
    "  appType - a string defining the type of the app\n"
    "  args - the command line args as string (sys.argv)\n"
    "  showWindow - whether to show the GUI window\n"
    "    (ignored in console mode)\n"
    "The function returns None"},

    {"stop", (PyCFunction)stop, METH_NOARGS,
    "Stops the RTUVCCam library.\n"
    "This should be called just before exiting.\n"
    "There are no parameters and the function returns None."},

    {"checkDaemonMode", (PyCFunction)checkDaemonMode, METH_NOARGS,
    "Returns True if '-d' was specified on command line"},

    {"vidCapOpen", (PyCFunction)vidCapOpen, METH_VARARGS,
    "Tries to open a camera. The camera is specified by a \n"
    "camera number starting from 0.\n"
    "0 is equivalent to /dev/video0, 1 is /dev/video1 etc\n"
    "The function returns true if successful.\n"},

    {"vidCapClose", (PyCFunction)vidCapClose, METH_VARARGS,
    "Tries to close a camera. The camera is specified by a \n"
    "camera number starting from 0.\n"
    "0 is equivalent to /dev/video0, 1 is /dev/video1 etc\n"
    "The function returns true if successful.\n"},

    {"vidCapGetFrame", (PyCFunction)vidCapGetFrame, METH_VARARGS,
    "Tries to get a captured frame from a camera.\n"
    "The function takes the camera number as its parameter.\n"
    "It returns 6 values:\n"
    "  valid - True or False depending on whether the call succeeded\n"
    "  frame - captured frame (could be jpeg or uncompressed)\n"
    "  jpeg - True if frame is jpeg compressed, False for uncompressed\n"
    "  width - width of frame\n"
    "  height - height of frame\n"
    "  rate - frame rate\n"},

    {"setWindowTitle", (PyCFunction)setWindowTitle, METH_VARARGS,
    "Sets the window title in GUI mode.\n"
    "The parameter is a string containing the new window title.\n"
    "The function returns None"},

    {"displayImage", (PyCFunction)displayImage, METH_VARARGS,
    "Displays an uncompressed image in the GUI window.\n"
    "There are four parameters:\n"
    "  image - the image as a string\n"
    "  width - the width of the image\n"
    "  height - the height of the image\n"
    "  timestamp - a string containing the timestamp (can be empty)\n"
    "The function returns None"},

    {"displayJpegImage", (PyCFunction)displayJpegImage, METH_VARARGS,
    "Displays a Jpeg image in the GUI window.\n"
    "There are two parameters:\n"
    "  image - the Jpeg image as a string\n"
    "  timestamp - a string containing the timestamp (can be empty)\n"
    "The function returns None"},

    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initRTUVCCam()
{
    Py_InitModule3("RTUVCCam", RTUVCCamMethods, "RTUVCCam library");
}
