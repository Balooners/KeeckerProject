# Public Sources

**Status:** In Progress
**Last update:** 2026-10-28

## Objective

List the public, non-device sources used to understand the Keecker K1 as a product: what it did, how it was built, and how it ended. Device acquisitions (ADB, APK, ODEX) are documented elsewhere.

## Rules

- Keecker documents are copyrighted by KEECKER SAS. They are **referenced, not redistributed**: URL, archive snapshot and SHA256 of the downloaded copy.
- Local copies live outside the repository.
- Content from these sources is summarised in our own words in [FEATURES.md](../04-Analysis/FEATURES.md) and [platform.md](../07-Hardware/platform.md).

## Official Keecker source code (public, GitHub)

| Repository | Content | License | Last activity |
|---|---|---|---|
| https://github.com/keecker/services-api | Android SDK: 36 AIDL Binder contracts (projector, perception, movement), client classes, `embedded/stm` safety status | Apache 2.0 (`LICENSE.md`, KEECKER SAS 2012-2018) | 2019-11 |
| https://github.com/keecker/remote-api | Robot ↔ companion app protocol: 23 protobuf files (~180 messages), libsodium authentication design | No license file: read and document only | 2019-02 |
| https://github.com/gallagth/keecker_kernel | Linux 3.0 kernel, branch `wandboard/jb4.3_1.1.0-ga__wandboard` (i.MX6, Android 4.3), commits by "keecker" in Feb 2014 | GPL-2.0 (kernel `COPYING`) | 2014-02 |

`gallagth/keecker_kernel` is a 2014 prototype on a Wandboard (NXP i.MX6). It is **not** the production K1 platform (Snapdragon 820). ✅ Confirmed from its branch name and commit history.

Other `keecker` GitHub repositories (`ParallaxHeader`, `XLPagerTabStrip`) are mobile UI libraries unrelated to the robot.

## developer.keecker.com (live on 2026-10-28)

Official developer portal, still online (HTTP 200 on 2026-10-28). Archived since 2017 on the Wayback Machine.

- Overview: the Keecker Android SDK gives apps access to the front and 360° cameras, the depth camera and proximity sensors, movement commands, map location, and wall and charging station detection. Apps can be distributed to Keecker owners through Google Play. It also mentions two other developer options: **Blockly** (automation) and a **ROS application** (robot algorithm prototyping).
- Guide "Creating a Keecker app": Android TV app, dependency `com.github.keecker:services-api:0.2.0-alpha` from JitPack, permission `com.keecker.permission.PROJECTION`, `ProjectorClient.setState(ProjectorState(orientation = 0 | 90))`. Development is done through **a USB port located under the robot, at the back**, with an on-screen confirmation.
- Reference 0.2 (Dokka): packages `com.keecker.hardware.robot.interfaces`, `com.keecker.services.interfaces`, `com.keecker.services.navigation.interfaces` (odometry, compass, align-to-wall, go-to-charging-station status `STARTED / DOCKING / DOCKED / FAILED`, kidnapping status, detection results).

## keecker.com (Internet Archive)

| Document | Original URL | Snapshot | SHA256 of local copy |
|---|---|---|---|
| Support Q&A, 85 pages, generated 2019-02-22 | Google Drive file `10VaW9KDYL7kL2ifj2-d9B4r-gvXSFamt`, linked from the support page | live Drive (2026-10-28) | `c42b329b63a31b1181decc98bcdad4966610514c1127ddbdc56269c2d892253c` |
| FAQ (2014 Kickstarter era), 7 pages | `http://www.keecker.com/download/keecker_faq.pdf` | Wayback | `b47e2b21841a9ceb98d6dc5f6f23be1e9edf82424328e04f651de7520cbc10d6` |
| Press release | `http://www.keecker.com/download/keecker_pressrelease.pdf` | Wayback | `f9c42798baa0041f5140b46f5bd4ee3174acd03f1f4cf5ba3065d0bbcbfa81b3` |
| Embedded software engineer job offer | `http://www.keecker.com/download/embedded_software_engineer_keecker.pdf` | Wayback | `578fac11e17dfe5015b604c9bbff05cf066dce50fc462427072bf2f794ef38f0` |
| Specifications page | `https://www.keecker.com/eu-en/specifications` | Wayback | - |
| End-of-life support page | `https://www.keecker.com/eu-en/support` | Wayback `20210804003348` | - |
| Setup steps | `http://www.keecker.com/eu-en/setup` | Wayback | - |
| Professional offer | `https://www.keecker.com/eu-fr/pro` | Wayback | - |
| Blog #9 "Les algorithmes de Keecker pour la navigation autonome" (2018) | `https://www.keecker.com/eu-fr/blog/Les-algorithmes-de-Keecker-pour-la-navigation-autonome` | Wayback | - |
| Blog #2 "Keecker, le robot qui évolue en permanence" (2018) | `https://www.keecker.com/eu-fr/blog/Keecker-produit-evolution` | Wayback | - |
| Other blog posts (Alexa, voice notifications and video call, games, Jenkins to GitLab CI, demos, beta) | `https://www.keecker.com/eu-fr/blog/` | Wayback | - |

Acquisition command for archived pages: `curl -L https://web.archive.org/web/2020id_/<original URL>` (the `id_` suffix returns the original content without the archive toolbar).

## End-of-life documents (Google Docs, live on 2026-10-28)

Linked from the support page, in Drive folder `1B6pcO9AxroiW-lEsOLPIBSSPk13zCGAo`:

- "FAQ Connect another smartphone or Tablet": document `1SmoTLGR7U5l8W4smEX2SJWxDji-jcP5PYJV_q1tFk6w`
- "FAQ factory reset and updates to turn off": document `1w4kzGHMOzrMtxauBrijbGnioNehC6-jRLBE-Xeqs-Oc`
- "FAQ Spotify Youtube Netflix": document `1DnVIzkLSN8VCj1PC50yvkxbnc6vb4YUrL8yBuOXPedE`
- "Last release communication" and "Support EN - Keecker.pdf"

Acquisition command: `curl -L "https://docs.google.com/document/d/<id>/export?format=txt"`.

## Community

- Reddit: https://www.reddit.com/r/keecker (linked by Keecker's end-of-life support page). Not yet reviewed: the site blocks automated access.

## Press (secondary sources, lower confidence)

- New Atlas, consumer launch (2017): https://newatlas.com/keecker-consumer-launch/51619/
- Engadget, CES 2014 hands-on: https://www.engadget.com/2014-01-09-keecker-hands-on.html
- Fast Company, Kickstarter (2014): https://www.fastcompany.com/3037081/ex-googlers-robotic-butler-launches-on-kickstarter
- originofbots.com shutdown article: https://www.originofbots.com/news/keecker-shuts-down-after-6-years-robots-get-final-ota-update-march-2026. 🔴 Treat as unreliable: its dates (final OTA in March 2026) contradict the archived support page, captured in August 2021, which already describes the final release.

## Open Questions

- Year of the final "March 8th" release. The support page describing it was archived in August 2021, so the release predates that capture.
- FCC filing: no FCC ID found yet. Read it on the robot's regulatory label, then search the FCC database for internal photos.
- Kickstarter campaign page and updates (2014-2017) not yet reviewed.
