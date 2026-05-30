PORTNAME=	elytambiance
DISTVERSION=	0.5.1
CATEGORIES=	audio

MAINTAINER=	elytraVIII@gmail.com
COMMENT=	Ambient sound generator for GhostBSD
WWW=		https://github.com/elytraVIII/ElytAmbience

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}pygobject>=3.0:devel/py-pygobject@${PY_FLAVOR} \
		gstreamer1-plugins-good>=0:multimedia/gstreamer1-plugins-good \
		gstreamer1-plugins-ogg>=0:multimedia/gstreamer1-plugins-ogg \
		gstreamer1-plugins-vorbis>=0:multimedia/gstreamer1-plugins-vorbis

USES=		gettext-runtime gnome meson python:3.11+
USE_GNOME=	gtk30 glib20
USE_GITHUB=	yes
GH_ACCOUNT=	elytraVIII
GH_PROJECT=	ElytAmbience
GH_TAGNAME=	v${DISTVERSION}

.include <bsd.port.mk>
