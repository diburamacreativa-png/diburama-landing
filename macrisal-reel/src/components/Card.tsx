import React from 'react';
import {Freeze, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {CARD_LABELS, CLIPS, COLORS, FONTS, SOURCES, TIMING, sec} from '../config';
import {CardSpec, LABEL_RANGES, Rect} from '../choreography';
import {ease, track} from '../lib/motion';

// Posición de la ventana en un fotograma: un muelle por movimiento.
export const cardRect = (spec: CardSpec, frame: number): Rect => {
  const axis = (k: keyof Rect) => {
    const keys = spec.moves
      .filter((m) => m[k] !== undefined)
      .map((m) => ({at: sec(m.at), to: m[k] as number, dur: m.dur ?? TIMING.card}));
    return track(frame, spec.start[k], keys);
  };
  return {x: axis('x'), y: axis('y'), w: axis('w')};
};

// Fotograma de origen exacto: el fragmento empieza en `at` y se reproduce
// a velocidad original. Fuera de rango se congela en el borde (o se repite si loop).
const ClipFrame: React.FC<{clipId: keyof typeof CLIPS; at: number; loop?: boolean}> = ({
  clipId,
  at,
  loop,
}) => {
  const frame = useCurrentFrame();
  const clip = CLIPS[clipId];
  const len = sec(clip.out) - sec(clip.in); // salida exclusiva
  const raw = frame - sec(at);
  const local = loop ? ((raw % len) + len) % len : Math.min(Math.max(raw, 0), len - 1);
  return (
    <Freeze frame={local}>
      <OffthreadVideo
        src={staticFile(SOURCES[clip.src])}
        trimBefore={sec(clip.in)}
        muted
        style={{width: '100%', height: '100%', objectFit: 'cover', display: 'block'}}
      />
    </Freeze>
  );
};

export const Card: React.FC<{spec: CardSpec}> = ({spec}) => {
  const frame = useCurrentFrame();
  if (frame < sec(spec.life[0]) || frame >= sec(spec.life[1])) return null;

  const {x, y, w} = cardRect(spec, frame);
  const h = (w * 9) / 16;
  const active = [...spec.content].reverse().find((c) => frame >= sec(c.at)) ?? spec.content[0];
  const radius = Math.max(10, w * 0.026);
  const labelSize = Math.max(18, Math.min(24, w * 0.026));
  const range = LABEL_RANGES.find(([a, b]) => frame >= sec(a) && frame < sec(b));
  const showLabel = spec.label && w >= 420 && range !== undefined;
  // La etiqueta se despliega de izquierda a derecha al empezar el tramo.
  const labelReveal = range ? ease(frame, sec(range[0]) + 4, 8) : 0;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: radius,
        overflow: 'hidden',
        background: '#fff',
        zIndex: spec.z ?? 1,
        boxShadow:
          '0 0 0 1px rgba(20,20,20,0.06), 0 2px 6px rgba(20,20,20,0.06), 0 22px 48px -18px rgba(20,20,20,0.28)',
      }}
    >
      {/* key: cambiar de fragmento monta un vídeo nuevo, sin fundido */}
      <ClipFrame key={active.clip + active.at} clipId={active.clip} at={active.at} loop={active.loop} />
      {showLabel ? (
        <div
          style={{
            position: 'absolute',
            // Si la ventana sangra por la izquierda, la etiqueta se mantiene dentro del cuadro.
            left: Math.max(labelSize * 0.8, -x + 36),
            top: labelSize * 0.8,
            padding: `${labelSize * 0.3}px ${labelSize * 0.55}px`,
            borderRadius: labelSize * 0.3,
            background: 'rgba(20,20,20,0.86)',
            color: COLORS.light,
            fontFamily: FONTS.mono,
            fontWeight: 500,
            fontSize: labelSize,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            lineHeight: 1.2,
            clipPath: `inset(0 ${(1 - labelReveal) * 100}% 0 0)`,
          }}
        >
          {CARD_LABELS[CLIPS[active.clip].src]}
        </div>
      ) : null}
    </div>
  );
};
