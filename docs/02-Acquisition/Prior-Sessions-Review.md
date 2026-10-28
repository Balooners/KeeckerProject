# Keecker K1 — Analyse d’état des lieux

> **Source note (2026-10-28):** review written by Harold's earlier ChatGPT analysis sessions, which did the first
> ADB and network work on the robot. Kept in its original French. Items marked SUPPOSÉ are recollections without
> recoverable raw output; they are re-checked by `scripts/robot-readonly-snapshot.ps1`
> ([adb-runbook.md](../10-Operations/adb-runbook.md)).
>
> Since this review, static analysis has confirmed several items it lists as INCONNU:
> `_keecker._tcp` and `/remote/keecker.ws` (official app and robot DEX,
> [remote-app-protocol.md](../05-Interfaces/remote-app-protocol.md)), `/dev/ttyHSL1` and `/dev/resetboard` as paths
> used by `libhw_robot_jni.so` ([stm32-protocol.md](../05-Interfaces/stm32-protocol.md); presence on the device still
> to check), and `boot.oat`, which was extracted (`firmware/oat/`, see [SESSION_STATE.md](../../SESSION_STATE.md)).
>
> 🟡 Notable: a past `getprop` reportedly showed verified boot **green**. On Qualcomm Android 7 devices, `green`
> normally means a locked bootloader with a verified image. This must be confirmed with `ro.boot.flash.locked` and
> `ro.oem_unlock_supported`.

## Règle de qualification

- **OBSERVÉ** : sortie brute effectivement vue dans la conversation ou fait explicitement documenté dans le *Keecker Engineering Handbook v1.0*.
- **SUPPOSÉ** : déduction, connaissance générale, ou valeur rapportée auparavant sans sortie brute récupérable.
- **INCONNU** : jamais vérifié ou aucune preuve exploitable retrouvée.

---

## 1. Bootloader

Commandes recherchées :

```sh
getprop ro.boot.flash.locked
getprop ro.boot.verifiedbootstate
getprop ro.boot.veritymode
getprop ro.oem_unlock_supported
getprop sys.oem_unlock_allowed
getprop ro.bootloader
```

**INCONNU** : aucune sortie brute prouvant que ces six commandes ont été exécutées individuellement n’est récupérable.

Une information avait été rapportée lors d’un `getprop` général :

```text
verified boot green
```

Mais la ligne brute originale n’est plus disponible.

- `ro.boot.verifiedbootstate` : **SUPPOSÉ / compte-rendu antérieur** → probablement `green`
- `ro.boot.flash.locked` : **INCONNU**
- `ro.boot.veritymode` : **INCONNU**
- `ro.oem_unlock_supported` : **INCONNU**
- `sys.oem_unlock_allowed` : **INCONNU**
- `ro.bootloader` : **INCONNU**

Conclusion : l’état réel de verrouillage du bootloader n’est pas établi.

---

## 2. Type de build

Valeurs rapportées lors de l’analyse précédente :

```text
ro.build.type=user
ro.secure=1
ro.debuggable=0
```

La sortie brute originale n’est plus disponible, donc elles sont classées comme suit :

| Propriété | Statut | Valeur |
|---|---|---|
| `ro.build.type` | SUPPOSÉ / compte-rendu antérieur | `user` |
| `ro.build.tags` | INCONNU | — |
| `ro.debuggable` | SUPPOSÉ / compte-rendu antérieur | `0` |
| `ro.secure` | SUPPOSÉ / compte-rendu antérieur | `1` |
| `ro.build.fingerprint` | INCONNU | — |
| `ro.build.display.id` | INCONNU | — |

Autres informations rapportées depuis ce même `getprop` général :

```text
Android 7.0
SDK 24
build 100140002
04/03/2019
Keecker/keecker_k1_mb02
service.adb.tcp.port=5555
```

**SUPPOSÉ / compte-rendu antérieur** : ces valeurs sont cohérentes avec notre analyse, mais la sortie brute exacte n’est plus récupérable.

---

## 3. Matériel

Éléments identifiés lors de l’analyse précédente :

```text
Qualcomm MSM8996
Snapdragon 820
Keecker K1
```

Chaîne également rapportée :

```text
Keecker/keecker_k1_mb02
```

Statut : **SUPPOSÉ / compte-rendu antérieur** pour les valeurs précises de propriétés Android, car la sortie brute n’est plus disponible.

Propriétés exactes demandées :

```text
ro.product.board
ro.board.platform
ro.hardware
ro.product.model
ro.product.device
```

**INCONNU** : valeurs brutes non retrouvées.

Fichiers Device Tree :

```sh
cat /proc/device-tree/model
cat /proc/device-tree/compatible
```

**INCONNU** : aucune preuve récupérable qu’ils aient été lus.

---

## 4. Noyau

Commandes recherchées :

```sh
uname -a
cat /proc/version
```

**INCONNU** : aucune sortie brute retrouvée et aucune preuve suffisante que ces commandes aient été exécutées.

À vérifier :

- version du noyau Linux ;
- architecture exacte ;
- chaîne de compilation ;
- date de build ;
- éventuels patches constructeur.

---

## 5. Partitions

Commandes recherchées :

```sh
ls -l /dev/block/bootdevice/by-name
cat /proc/partitions
```

**INCONNU** : aucune liste brute retrouvée.

Nous ne pouvons donc pas confirmer la présence ni la disposition exacte des partitions classiques telles que :

```text
boot
recovery
system
userdata
aboot
modem
persist
cache
```

Conclusion : la cartographie des partitions reste à faire avant toute tentative de dump ou modification firmware.

---

## 6. Fastboot / Bootloader / Recovery / EDL

Commandes recherchées :

```sh
adb reboot bootloader
fastboot devices
fastboot oem device-info
fastboot getvar all
```

**INCONNU** : aucune sortie brute récupérable ne prouve qu’elles aient été exécutées.

Même statut pour :

- démarrage manuel en **Recovery** ;
- entrée en **Qualcomm EDL** ;
- apparition d’un périphérique **Qualcomm HS-USB QDLoader 9008**.

Conclusion : nous ne pouvons pas affirmer que Fastboot, Recovery ou EDL fonctionnent, ni qu’ils sont absents.

---

## 7. Option « Déverrouillage OEM »

**INCONNU**.

Aucune observation fiable ne permet d’affirmer que les Options pour les développeurs affichent :

```text
Déverrouillage OEM
```

La présence d’ADB ne suffit pas à déduire l’existence de cet interrupteur.

---

## 8. Accès root / `adb root` / `su`

### OBSERVÉ — ADB en USB

```text
252B203062917005134     device
```

### OBSERVÉ — passage en Wi‑Fi

```text
adb disconnect
disconnected everything
```

Puis :

```text
adb connect 192.168.1.191:5555
connected
```

Et :

```text
adb devices
192.168.1.191:5555 device
```

Nous avions également vu précédemment :

```text
failed to authenticate
```

et :

```text
192.168.1.191:5555 unauthorized
```

Le *Keecker Engineering Handbook v1.0* consigne également explicitement l’état :

```text
ADB 5555 unauthorized
```

Commandes recherchées :

```sh
adb root
which su
ls -l /system/xbin/su
ls -l /system/bin/su
```

**INCONNU** : aucune sortie brute retrouvée.

Conclusion : nous n’avons pas de preuve que le robot ait fourni un shell root, ni que `su` soit présent.

---

## 9. Ports série et périphériques matériels

Commandes recherchées :

```sh
ls -l /dev
ls -l /dev/ttyHSL*
ls -l /dev/ttyHS*
ls -l /dev/resetboard
cat /proc/tty/drivers
```

**INCONNU** : aucune sortie brute retrouvée.

En particulier, l’existence de :

```text
/dev/resetboard
```

n’est pas démontrée à ce stade.

À vérifier :

- interfaces série Qualcomm ;
- éventuels TTY debug ;
- ports console ;
- périphériques spécifiques Keecker ;
- driver lié au reset board.

---

## 10. Réseau

### OBSERVÉ / documenté

Ports confirmés :

```text
5555
8008
8009
8080
8443
9000
```

Le *Keecker Engineering Handbook v1.0* les consigne comme ports confirmés.

Identification documentée :

```text
8080 = File Uploader
Jetty + React
```

et :

```text
8008 = Google Cast / DIAL
```

Pour le service mDNS :

```text
_keecker._tcp
```

**INCONNU** : aucune trace brute récupérable ne permet d’affirmer qu’il a été observé.

Pour l’URL :

```text
/remote/keecker.ws
```

**INCONNU** : aucune observation brute récupérable ne permet de confirmer qu’elle a été trouvée.

---

## 11. Fichiers extraits du robot

### OBSERVÉ

Fichier confirmé :

```text
com.keecker.services.odex
```

Taille rapportée :

```text
70,189,776 bytes
```

Il provenait de l’arborescence de l’application :

```text
com.keecker.services
```

Commande utilisée :

```sh
adb pull .../com.keecker.services.odex
```

**Important** : le chemin source complet n’est plus récupérable, donc il ne faut pas l’inventer.

Autres éléments :

- plusieurs **APK** avaient été extraits, mais noms, chemins et commandes exacts ne sont plus récupérables ;
- `boot.oat` : **INCONNU** ;
- autres ODEX : **INCONNU** faute de liste brute exploitable.

Conclusion : seul `com.keecker.services.odex` est confirmé avec suffisamment de confiance pour être cité ici.

---

## 12. Autres conclusions importantes

### OBSERVÉ / documenté

Versions :

```text
Services Keecker : 1.14.6
App : 2.0.3
```

Activités Keecker identifiées :

```text
TouchWallActivity
ProjectionActivity
PlayerActivity
DiagnosticActivity
UpdateActivity
PostSetupActivity
PreSetupActivity
```

Le Handbook les conserve explicitement comme références du projet.

### SUPPOSÉ / compte-rendu antérieur

Packages / composants déjà identifiés dans notre analyse :

```text
com.keecker.services
com.keecker.ota
com.keecker.apps.data
com.keecker.diagnostic
com.keecker.launcher_netflix
```

Services rapportés :

```text
KeeckerRegistryService
IhmService
RecoveryService
```

Ils restent classés **SUPPOSÉ / compte-rendu antérieur** tant que les sorties `pm`, `dumpsys` ou équivalentes ne sont pas retrouvées.

### Conclusion générale

La couche Android, applicative et réseau a déjà été significativement explorée.

En revanche, la couche bas niveau reste largement à cartographier :

```text
état réel du bootloader
OEM unlock
fastboot
recovery
EDL
partitions
kernel
root / su
device-tree
ports série / périphériques Qualcomm
```

Ce sont les points à prioriser lors de la prochaine session physique sur le robot.

---

## Résumé — 5 lignes maximum

- **CERTAIN** : ADB fonctionne en USB puis en Wi‑Fi ; `192.168.1.191:5555 device` a été observé.
- **CERTAIN** : ports `5555/8008/8009/8080/8443/9000` documentés ; `8080 = File Uploader Jetty/React`, `8008 = Cast/DIAL`.
- **CERTAIN** : `com.keecker.services.odex` a été extrait ; Services `1.14.6` et App `2.0.3` sont documentés.
- **À VÉRIFIER** : propriétés bootloader/build/hardware exactes, noyau, Device Tree, partitions, root/su, option « Déverrouillage OEM ».
- **À VÉRIFIER** : Fastboot, Recovery, EDL 9008, `/dev/tty*`, `_keecker._tcp` et `/remote/keecker.ws`.
