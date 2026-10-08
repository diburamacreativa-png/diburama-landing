import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, FONTS, SEGMENTS, Theme, TIMING, sec} from '../config';
import {ease, maskShift} from '../lib/motion';

// Línea con máscara: entra desde abajo y sale hacia arriba.
export const MaskLine: React.FC<{
  inAt: number;
  outAt: number | null;
  children: React.ReactNode;
  style?: React.CSSProperties;
  inDur?: number;
  outDur?: number;
}> = ({inAt, outAt, children, style, inDur = TIMING.titleIn, outDur = TIMING.titleOut}) => {
  const frame = useCurrentFrame();
  const shift = maskShift(frame, inAt, inDur, outAt, outDur);
  if (shift >= 108 || shift <= -108) return null;
  return (
    <div style={{overflow: 'hidden', paddingBottom: '0.14em', marginBottom: '-0.14em', ...style}}>
      <div style={{transform: `translateY(${shift}%)`, whiteSpace: 'nowrap'}}>{children}</div>
    </div>
  );
};

// Agrupa segmentos consecutivos con el mismo valor (título o etiqueta).
const blocks = <T,>(get: (s: (typeof SEGMENTS)[number]) => T, same: (a: T, b: T) => boolean) => {
  const out: {from: number; to: number; value: T; theme: Theme}[] = [];
  for (const s of SEGMENTS) {
    const last = out[out.length - 1];
    if (last && same(last.value, get(s))) last.to = s.to;
    else out.push({from: s.from, to: s.to, value: get(s), theme: s.theme});
  }
  return out;
};

const END = SEGMENTS[SEGMENTS.length - 1].to;

// El signo final "?" se marca en rojo como acento.
const withAccent = (line: string) => {
  if (!line.endsWith('?')) return line;
  return (
    <>
      {line.slice(0, -1)}
      <span style={{color: COLORS.accent}}>?</span>
    </>
  );
};

export const Titles: React.FC = () => {
  const frame = useCurrentFrame();
  const list = blocks((s) => s.title, (a, b) => a.join('|') === b.join('|'));
  return (
    <>
      {list.map((b, bi) => {
        if (!b.value.length) return null;
        const enter = sec(b.from) + (bi === 0 ? -3 : 3);
        const exit = b.to >= END ? null : sec(b.to);
        if (frame < sec(b.from) || (exit !== null && frame > exit + TIMING.titleOut + 2)) return null;
        return (
          <div
            key={bi}
            style={{
              position: 'absolute',
              left: 80,
              top: 262,
              width: 940,
              fontFamily: FONTS.display,
              fontWeight: 600,
              fontSize: 132,
              lineHeight: 1.0,
              letterSpacing: '-0.045em',
              color: b.theme === 'dark' ? COLORS.light : COLORS.dark,
            }}
          >
            {b.value.map((line, i) => (
              <MaskLine
                key={i}
                inAt={enter + i * TIMING.lineStagger}
                outAt={exit === null ? null : exit + i * 1}
              >
                {withAccent(line)}
              </MaskLine>
            ))}
          </div>
        );
      })}
    </>
  );
};

export const Kickers: React.FC = () => {
  const frame = useCurrentFrame();
  const list = blocks((s) => s.kicker, (a, b) => a === b);
  return (
    <>
      {list.map((b, bi) => {
        if (!b.value) return null;
        const exit = b.to >= END ? null : sec(b.to);
        if (frame < sec(b.from) || (exit !== null && frame > exit + 10)) return null;
        return (
          <div
            key={bi}
            style={{
              position: 'absolute',
              left: 82,
              top: 212,
              fontFamily: FONTS.mono,
              fontWeight: 500,
              fontSize: 26,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              color: b.theme === 'dark' ? COLORS.mutedOnDark : COLORS.mutedOnLight,
            }}
          >
            <MaskLine inAt={sec(b.from) + (bi === 0 ? 0 : 1)} outAt={exit} inDur={8} outDur={6}>
              {b.value}
            </MaskLine>
          </div>
        );
      })}
    </>
  );
};

// Regla roja: se dibuja de izquierda a derecha y se recoge hacia la derecha.
export const Rule: React.FC<{x: number; y: number; w: number; inAt: number; outAt: number | null}> = ({
  x,
  y,
  w,
  inAt,
  outAt,
}) => {
  const frame = useCurrentFrame();
  const pin = ease(frame, inAt, 12);
  const pout = outAt === null ? 0 : ease(frame, outAt, 8);
  if (pin <= 0 || pout >= 1) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: x + w * pout,
        top: y,
        width: w * (pin - pout),
        height: 6,
        background: COLORS.accent,
      }}
    />
  );
};
