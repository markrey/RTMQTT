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

#ifndef RTUVCCAMGLUE_H
#define RTUVCCAMGLUE_H

class RTUVCCamMain;

class RTUVCCamGlue
{
public:
    RTUVCCamGlue();
    virtual ~RTUVCCamGlue();

    //  functions called from Python

    bool vidCapOpen(int cameraNum, int width, int height, int rate);
    bool vidCapClose(int cameraNum);
    bool vidCapGetFrame(int cameraNum, unsigned char** frame, int& length, bool& jpeg,
                                             int& width, int& height, int& rate);

    void startLib(int& argc, char **argv, bool showWindow);
    void stopLib();
    bool checkDaemonMode() { return m_daemonMode;}          // checks if in daemon mode
    void setWindowTitle(char *title);                       // sets the window title in GUI mode
    void displayImage(unsigned char *image, int length,
                      int width, int height, char *timestamp); // displays an image in GUI mode
    void displayJpegImage(unsigned char *image, int length, char *timestamp); // displays a Jpeg in GUI mode
    char *getAppName();                                     // returns the app name

 private:
    RTUVCCamMain *m_main;

    bool m_daemonMode;

    int m_argc;
    char **m_argv;
};

#endif // RTUVCCAMGLUE_H

