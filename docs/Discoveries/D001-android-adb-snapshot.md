# D001 - Première cartographie Android du Keecker K1

## Date

2026-06-28

## Objectif

Établir une première cartographie technique du système Android embarqué.

---

# Plateforme

| Élément | Valeur |
|---------|--------|
| Robot | Keecker K1 |
| Android | 7.0 |
| API Level | 24 |
| SoC | Qualcomm Snapdragon 820 (MSM8996) |
| Architecture | arm64-v8a |

---

# Accès

ADB USB : OK

ADB Wi-Fi : OK

Connexion :

```bash
adb connect <IP>:5555
```

---

# Binder Services

133 Binder Services détectés.

Services propriétaires identifiés :

- KeeckerRegistryService
- IhmService
- RecoveryService

---

# APK propriétaires

| Package | Taille |
|----------|----------|
| com.keecker.services | 148 MB |
| com.keecker.apps.data | 66 MB |
| com.keecker.apps.diagnostic | 6.7 MB |
| com.keecker.services.ota | 640 KB |
| com.keecker.apps.launcher_netflix | 496 KB |
| K1_TvSetupCustomizer | 206 KB |
| K1_LeanbackCustomizer | 1.18 MB |
| KeeckerLeanbackWidget | 28 KB |

Toutes les APK ont été extraites via ADB.

---

# Architecture logicielle

Le système repose sur une architecture de services Android.

Services identifiés :

- Backend
- Media
- Remote
- HttpServer
- Optimized
- Notification
- Presence
- Planner
- Security
- Voice
- Projection
- Navigation
- TouchWall
- Conference
- System

---

# Robotique

Services dédiés :

- SlamService
- MovementPlannerService
- MovementPerceptionService
- PerceptionService
- FollowMeService
- HwRobotService

---

# Vision

Services :

- CameraService
- ZcamService

---

# Contrôle matériel

Le HwRobotService expose notamment :

- contrôle moteurs
- tilt projecteur
- focus
- ventilateurs
- calibrations IR
- coefficients PID
- gestion batterie

---

# Bibliothèques natives

Découverte majeure :

Le cœur du robot est implémenté en C/C++ via JNI.

Bibliothèques identifiées :

- libhw_robot_jni.so
- libslam.so
- libmovement_planner.so
- libperception.so
- liblocalizer.so
- libodometry_jni.so
- libnative_camera_jni.so
- libobject_detector_jni.so
- libtensorflow_inference.so
- libopencv_*.so
- libroscpp_serialization.so
- libtf2.so

---

# Premières conclusions

Le Keecker repose sur une architecture hybride :

Android
↓
Services Binder
↓
Services Java
↓
JNI
↓
Bibliothèques natives C++
↓
ROS
↓
STM32
↓
Actionneurs

Cette architecture est nettement plus avancée qu'attendu pour un produit commercial de 2017.