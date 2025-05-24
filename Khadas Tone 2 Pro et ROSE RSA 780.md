﻿\*\*\* /udev/rules.d/60-persistent-cdrom-rsa780.rules \*\*\*

\# Règle pour lecteur CD ROSE RSA780: Lance cd\_handler et permissions

\# Cible le périphérique bloc srX dont le parent USB a les bons IDs

ACTION=="add", SUBSYSTEM=="block", KERNEL=="sr[0-9]\*", SUBSYSTEMS=="usb", ATTRS{idVendor}=="13fd", >ACTION=="remove", SUBSYSTEMS=="usb", ATTRS{idVendor}=="13fd", ATTRS{idProduct}=="3940", RUN+="/usr/>

\# Notes:

\# - J'ai séparé les règles ADD et REMOVE pour plus de clarté.

\# - La règle ADD attend qu'un CD audio soit présent (ENV{ID\_CDROM\_MEDIA\_TRACK\_COUNT\_AUDIO}=="?\*") a># - La règle REMOVE cible directement le périphérique USB parent.

\# - J'ai remis GROUP et MODE pour assurer les permissions.

\# - Le SYMLINK est retiré pour l'instant car il posait problème.


\*\*\* /wireplumber/main.lua.d/99-khadas-tone2-pro-bitperfect.lua \*\*\*\*

-- Configuration spécifique pour KHADAS Tone 2 Pro

rule\_khadas\_tone2\_nodes = {

matches = {

{

-- Cible tous les nœuds (Sinks/Sources) liés à cette carte ALSA

{ "node.alsa.card.name", "equals", "Tone2 Pro" },

},

-- On peut ajouter une condition pour ne cibler que les Sinks si besoin:

-- {

--   { "node.alsa.card.name", "equals", "Tone2 Pro" },

--   { "media.class", "equals", "Audio/Sink" }

-- },

},

apply\_properties = {

-- == Propriétés spécifiques au Nœud ==

["node.nick"] = "KHADAS Tone2 Pro (Bit-Perfect)",        -- Nom court visible

["node.description"] = "KHADAS Tone2 Pro (Bit-Perfect ALSA)", -- Nom long

-- == Configuration Bit-Perfect (sur le nœud si possible) ==

["api.alsa.soft-mixer"] = false,

["api.alsa.soft-volumes"] = false,

["api.alsa.resample"] = false,

["channelmix.normalize"] = false,

["channelmix.mix-lfe"] = false,

["session.suspend-timeout-seconds"] = 0,

["monitor.channel-volumes"] = false,

-- == Priorité (peut aussi être appliquée ici) ==

["priority.driver"] = 2000,

["priority.session"] = 2000,

-- Assurer le profil Pro Audio si disponible sur le \*noeud\*

-- ["audio.profile"] = "pro-audio", -- A tester si besoin

-- Forcer le nœud à être le défaut (alternative aux priorités)

["node.autoconnect"] = true,

["priority.master"] = 2000, -- Autre façon d'influencer le défaut

},

}

table.insert(alsa\_monitor.rules, rule\_khadas\_tone2\_nodes)

-- Le bloc pour désactiver la carte interne reste inchangé et optionnel

--[[

rule\_disable\_internal\_card = { ... }

table.insert(alsa\_monitor.rules, rule\_disable\_internal\_card)

--]]
