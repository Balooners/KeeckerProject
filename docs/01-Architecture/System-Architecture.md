\# System Architecture



\*\*Status:\*\* In Progress



\*\*Last update:\*\* 2026-06-28



\---



\# Overview



Current understanding of the Keecker K1 architecture.



```text

Android Applications

&#x20;       │

Binder Services

&#x20;       │

Android Services

&#x20;       │

JNI

&#x20;       │

Native Libraries

&#x20;       │

ROS / OpenCV / TensorFlow

&#x20;       │

STM32

&#x20;       │

Hardware

```



\---



\# Android Layer



Confirmed:



\* Android 7.0

\* SDK 24

\* System application

\* Persistent services



\---



\# Binder Layer



Confirmed proprietary services:



\* KeeckerRegistryService

\* IhmService

\* RecoveryService



\---



\# Native Layer



Confirmed libraries:



\* libhw\_robot\_jni.so

\* libslam.so

\* libslam\_jni.so

\* libmovement\_planner.so

\* libmovement\_perception\_jni.so

\* libperception.so

\* liblocalizer.so

\* libnative\_camera\_jni.so

\* libobject\_detector\_jni.so



\---



\# Robotics



Confirmed technologies:



\* ROS

\* SLAM

\* Navigation

\* Perception

\* Follow Me



\---



\# Artificial Intelligence



Confirmed:



\* TensorFlow

\* OpenCV DNN



\---



\# Hardware



Confirmed:



\* Qualcomm Snapdragon 820

\* ARM64

\* STM32 (through HwRobotService)



\---



\# Evidence



\* AndroidManifest.xml

\* Binder service list

\* APK extraction

\* ODEX extraction

\* Native libraries



\---



\# Open Questions



\* JNI interfaces

\* STM32 protocol

\* ROS topology

\* Hardware buses

\* Internal APIs



