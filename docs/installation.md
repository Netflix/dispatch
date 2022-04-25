# Installation

Dispatch relies on multiple services to work, which are all orchestrated by `Docker Compose`.

### Requirements

- [Docker](https://www.docker.com/) 17.05.0+
- [Docker Compose](https://docs.docker.com/compose/) 1.19.0+
- A dedicated \(sub\)domain to host Dispatch on \(for example, dispatch.yourcompany.com\).
- At least 2400MB memory
- 2 CPU Cores

## Installing Dispatch Server

We strongly recommend using Docker for installing Dispatch and all its services. If you need to do something custom, you can use this repository as the basis of your setup. If you do not wish to use the Docker images we provide, you can still find Dispatch on PyPI; however, we don't recommend that method. You'll need to work your way back from the main Dispatch image. It is not too hard, but you are likely to spend a lot more time and hit some bumps.

To install Dispatch from the repository, clone the repository locally:

```bash
git clone https://github.com/Netflix/dispatch-docker.git
```

Before starting the installation, we strongly recommend you check out [how to configure your Dispatch instance](configuration/) as you'd need to rebuild your images \(`docker-compose build`\) if you want to change your configuration settings. You may copy and edit the example configs provided in the repository. If none exists, the install script will use these examples as actual configurations.

{% hint style="info" %}
Note: Dispatch will not start without at least a few required configuration variables. See the example [.env](https://github.com/Netflix/dispatch/blob/latest/docker/.env.example) configuration file.
{% endhint %}

{% hint style="info" %}
Note: Dispatch does not contain any data by default. For evaluation purposes, we do provide an example data set located [here](https://github.com/Netflix/dispatch/blob/master/data/dispatch-sample-data.dump). For instructions on how to restore this data, see [here](https://hawkins.gitbook.io/dispatch/administration-guide/cli#restore-dump).
{% endhint %}

To start, run the install script:

```bash
./install.sh
```

{% hint style="info" %}
Note: The `core` Docker service is not needed once the `web` and `schedule` services, which depend on it, are built.
{% endhint %}

### The "first" user problem

For any new Dispatch installation, new users are expected to register themselves via the `/auth/register` endpoint in the Dispatch UI. By default, users registering via this method are granted regular "user" permissions within Dispatch. There is no direct way through the UI to allow a user to obtain an "Owner" role (as no other Owners exist to grant them access).

For these users, we have a CLI command that allows users to be granted the role of their choosing:

```bash
docker exec -it dispatch_web_1 bash
dispatch user update --role Owner --organization <name-of-the-organization> <email-address-of-registered-user>
```

The default organization name in the sample data file is "default".

After one owner user has been established, they can grant this role to others via the UI.

## Going to Production

Before you deploy Dispatch to production, there are a few considerations and steps that should be taken.

### Basics

Because of the sensitivity of the information stored and maintained by Dispatch. You must follow standard host hardening practices:

- Run Dispatch with a limited user
- Disabled any unneeded services
- Enable remote logging
- Restrict access to the host

### Credential Management

Dispatch plugins require API tokens to communicate with third-party resources. These tokens are stored in either an environment variable or in the Dispatch `.env` file.

By default, these strings are in plain text, but Dispatch does provide hooks that allow for these credentials to be decrypted on server start. See the [Secret Provider](configuration/app.md#general) configuration option.

### Authentication

Dispatch provides a "Basic" authentication provider that controls access via a username and password combination to get going quickly. By default, this provider allows for **open registration**, which means that anyone will be able to create a Dispatch account if they have network access to your server.

Dispatch provides a "PKCE" authentication method to integrate existing and more robust SSO solutions for more robust authentication. See the [Authentication Provider](configuration/app.md#authentication)

### TLS/SSL

#### Nginx

Nginx is a popular choice to serve a Python project:

- It’s fast.
- It’s lightweight.
- Configuration files are simple.

Nginx doesn’t run any Python process; it only serves requests from outside to the Python server.

Therefore, there are two steps:

- Run the Python process.
- Run Nginx.

You will benefit from having:

- The possibility to have several projects listening to the port 80;
- Your web site processes won’t run with admin rights, even if –the user doesn’t work on your OS;
  -The ability to manage a Python process without touching Nginx or the other processes. It’s convenient for updates.

You must create an Nginx configuration file for Dispatch. On GNU/Linux, they usually go into `/etc/nginx/conf.d/`. Name it `dispatch.conf`.

proxy_pass passes the external request to the Python process. The port must match the one used by the Dispatch process.

You can make some adjustments to get a better user experience:

server_tokens off;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";

server {
listen 80;
return 301 https://$host$request_uri;
}

server {
listen 443;
access_log /var/log/nginx/log/dispatch.access.log;
error_log /var/log/nginx/log/dispatch.error.log;

location /api {
proxy_pass http://127.0.0.1:8000;
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
proxy_redirect off;
proxy_buffering off;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}

    location / {
        root /path/to/dispatch/static/dist;
        include mime.types;
        index index.html;
    }

}
Nginx will serve the favicon and static files, which it is much better at than python.

We recommended that you deploy TLS when deploying Dispatch. It may be obvious given Dispatch’s purpose, but the sensitive nature of Dispatch and what it controls makes this essential. A sample config for Dispatch that also terminates TLS:

{% hint style="info" %}
Some paths will have to be adjusted based on where you have chosen to install Dispatch.
{% endhint %}

```
server_tokens off;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";

server {
listen 80;
return 301 https://$host$request_uri;
}

server {
listen 443;
access_log /var/log/nginx/log/dispatch.access.log;
error_log /var/log/nginx/log/dispatch.error.log;

# certs sent to the client in SERVER HELLO are concatenated in ssl_certificate

ssl_certificate /path/to/signed_cert_plus_intermediates;
ssl_certificate_key /path/to/private_key;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;

# Diffie-Hellman parameter for DHE cipher suites, recommended 2048 bits

ssl_dhparam /path/to/dhparam.pem;

# modern configuration. tweak to your needs.

ssl_protocols TLSv1.1 TLSv1.2;
ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK';
ssl_prefer_server_ciphers on;

# HSTS (ngx_http_headers_module is required) (15768000 seconds = 6 months)

add_header Strict-Transport-Security max-age=15768000;

# OCSP Stapling ---

# fetch OCSP records from URL in ssl_certificate and cache them

ssl_stapling on;
ssl_stapling_verify on;

## verify chain of trust of OCSP response using Root CA and Intermediate certs

ssl_trusted_certificate /path/to/root_CA_cert_plus_intermediates;

resolver <IP DNS resolver>;

location /api {
proxy_pass http://127.0.0.1:8000;
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
proxy_redirect off;
proxy_buffering off;
proxy_set_header Host $host;
        proxy_set_header        X-Real-IP       $remote_addr;
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}

    location / {
        root /path/to/dispatch/static/dist;
        include mime.types;
        index index.html;
    }

}
```

Apache
An example apache config:

```
<VirtualHost \*:443>
...
SSLEngine on
SSLCertificateFile /path/to/signed_certificate
SSLCertificateChainFile /path/to/intermediate_certificate
SSLCertificateKeyFile /path/to/private/key
SSLCACertificateFile /path/to/all_ca_certs

    # intermediate configuration, tweak to your needs
    SSLProtocol             all -SSLv2 -SSLv3
    SSLCipherSuite          ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA
    SSLHonorCipherOrder     on

    # HSTS (mod_headers is required) (15768000 seconds = 6 months)
    Header always set Strict-Transport-Security "max-age=15768000"
    ...

# Set the dispatch DocumentRoot to static/dist

DocumentRoot /www/dispatch/dispatch/static/dist

# Uncomment to force http 1.0 connections to proxy

# SetEnv force-proxy-request-1.0 1

#Don't keep proxy connections alive
SetEnv proxy-nokeepalive 1

# Only need to do reverse proxy

ProxyRequests Off

# Proxy requests to the API to the dispatch service (and sanitize redirects from it)

ProxyPass "/api" "http://127.0.0.1:8000/api"
ProxyPassReverse "/api" "http://127.0.0.1:8000/api"

</VirtualHost>
```

{% hint style="info" %}
The above config is somewhat incomplete. If you have a working apache config, please let us know!
{% endhint %}

Also included in the configurations above are several best practices when it comes to deploying TLS. Things like enabling HSTS, disabling vulnerable ciphers are all excellent ideas for deploying Dispatch into a production environment.

For more SSL configuration options see: [Mozilla SSL Configuration Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/)
