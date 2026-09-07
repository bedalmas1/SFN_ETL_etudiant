# Configuration Mosquitto

Emplacement réservé à la configuration pédagogique du broker MQTT.

`mosquitto.conf` autorise l’accès anonyme uniquement parce que le port Compose est lié à `127.0.0.1`. Ne pas réutiliser cette configuration sur un hôte exposé.

## Broker protégé (séquence 7)

`mosquitto_protected.conf` désactive l’accès anonyme (`allow_anonymous false`) et impose `password_file` et `acl_file`, sur le port 1884, pour la démonstration « broker ouvert vs broker protégé ». `acl.conf` limite `capteur-lora` à la publication sur `airbase/#` et `superviseur` à l’abonnement en lecture sur `airbase/#`.

`passwd` contient les empreintes (PBKDF2-SHA512, format `$7$`), jamais les mots de passe en clair. Identifiants pédagogiques, valables uniquement sur ce laboratoire local :

| Utilisateur | Mot de passe | Droit accordé |
|---|---|---|
| `capteur-lora` | `s07-capteur-demo` | publication seule sur `airbase/#` |
| `superviseur` | `s07-superviseur-demo` | abonnement seul sur `airbase/#` |

Régénérer `passwd` si besoin :

```bash
docker run --rm -v "$(pwd)/docker/mosquitto:/mosquitto/config" --entrypoint mosquitto_passwd eclipse-mosquitto:2.0.22 -b -c /mosquitto/config/passwd capteur-lora s07-capteur-demo
docker run --rm -v "$(pwd)/docker/mosquitto:/mosquitto/config" --entrypoint mosquitto_passwd eclipse-mosquitto:2.0.22 -b /mosquitto/config/passwd superviseur s07-superviseur-demo
```

Ne jamais réutiliser ces identifiants au-delà de ce laboratoire local ; changer les mots de passe avant toute exposition au-delà de `127.0.0.1`.
