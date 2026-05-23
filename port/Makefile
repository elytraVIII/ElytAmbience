PORTNAME=	elytambiance
DISTVERSION=	0.2.0
CATEGORIES=	audio

MAINTAINER=	elytraVIII@gmail.com
COMMENT=	Ambient sound generator for GhostBSD
WWW=		https://github.com/elytraVIII/ElytAmbience

LICENSE=	MIT
LICENSE_FILE=	${WRKSRC}/LICENSE

RUN_DEPENDS=	${PYTHON_PKGNAMEPREFIX}gobject3>=0:devel/py-gobject3@${PY_FLAVOR} \
		gstreamer1-plugins-good>=0:multimedia/gstreamer1-plugins-good

USES=		gettext-runtime gnome meson python:3.11+
USE_GNOME=	gtk30 glib20
USE_GITHUB=	yes
GH_ACCOUNT=	elytraVIII
GH_PROJECT=	ElytAmbience

.include <bsd.port.mk>
