"""Spherical projection helpers for the Alsina reel.

All projections are azimuthal and centred on the nadir of the equirectangular
panorama. They belong to the general-perspective family, parametrised by `d`
(distance of the projection point from the sphere centre, in sphere radii):

    d = 0      gnomonic      -> virtual camera at the sphere centre (rectilinear)
    d = 1      stereographic -> "little planet"
    d -> inf   orthographic  -> the panorama seen as a real ball from outside

Radial law (normalised so the scale at the centre is 1):  r(theta) = (d+1) sin(theta) / (d + cos(theta))
"""
import numpy as np
import cv2


def srgb2lin(a):
    a = a.astype(np.float32) / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4).astype(np.float32)


def lin2srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)


def rotmat(yaw, pitch, roll):
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    Ry = np.array([[cr, 0, sr], [0, 1, 0], [-sr, 0, cr]])
    return Rz @ Rx @ Ry


def theta_from_rho(rho, d):
    """Inverse radial law: angle from nadir for normalised radius rho. Returns (theta, q); visible where q<1."""
    k = d + 1.0
    q = rho * d / np.sqrt(k * k + rho * rho)
    th = np.arctan2(rho, k) + np.arcsin(np.clip(q, -1, 1))
    return th, q


def rho_from_theta(th, d):
    return (d + 1.0) * np.sin(th) / (d + np.cos(th))


def directions(u, v, d):
    """u,v: normalised image-plane coords (centre scale 1). Returns unit vectors (...,3) and q."""
    rho = np.sqrt(u * u + v * v) + 1e-9
    th, q = theta_from_rho(rho, d)
    st = np.sin(th)
    X = st * u / rho
    Y = st * v / rho
    Z = -np.cos(th)
    return np.stack([X, Y, Z], -1).astype(np.float32), q


def azimuthal_maps(w, h, cx, cy, S, d, roll=0.0, R=np.eye(3), mirror=False):
    x = (np.arange(w, dtype=np.float32) - cx + 0.5)[None, :] / S
    y = (np.arange(h, dtype=np.float32) - cy + 0.5)[:, None] / S
    c, s = np.cos(roll), np.sin(roll)
    u = c * x - s * y
    v = s * x + c * y
    if mirror:
        u = -u
    P, q = directions(u, v, d)
    P = P @ np.asarray(R, np.float32).T
    lon = np.arctan2(P[..., 1], P[..., 0])
    lat = np.arcsin(np.clip(P[..., 2], -1, 1))
    return lon, lat, q < 1, q


def sample_equi(img, lon, lat, yaw_px=0.0, interp=cv2.INTER_CUBIC):
    H, W = img.shape[:2]
    mx = ((lon / (2 * np.pi) + 0.5) * W + yaw_px) % W - 0.5
    my = (0.5 - lat / np.pi) * H - 0.5
    return cv2.remap(img, mx.astype(np.float32), my.astype(np.float32), interp, borderMode=cv2.BORDER_WRAP)
