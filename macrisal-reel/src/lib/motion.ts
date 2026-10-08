import {spring} from 'remotion';
import {FPS} from '../config';

// Muelle críticamente amortiguado: arranque y frenada suaves, sin rebote.
// Devuelve 0 antes de `start` y 1 cuando termina (`dur` fotogramas).
export const ease = (frame: number, start: number, dur: number): number => {
  if (frame <= start) return 0;
  if (frame >= start + dur) return 1;
  return spring({
    frame: frame - start,
    fps: FPS,
    durationInFrames: dur,
    config: {damping: 200, mass: 1, stiffness: 120},
  });
};

export type Key<T> = {at: number; dur: number} & T;

// Valor con varios destinos: un muelle por cambio, cada uno con su inicio.
// Nunca se reinicia un muelle; los cambios se suman.
export const track = (
  frame: number,
  initial: number,
  keys: {at: number; to: number; dur: number}[],
): number => {
  let value = initial;
  let prev = initial;
  for (const k of keys) {
    value += (k.to - prev) * ease(frame, k.at, k.dur);
    prev = k.to;
  }
  return value;
};

// Revelado con máscara: % de desplazamiento vertical de una línea.
// Entra desde abajo y sale hacia arriba.
export const maskShift = (
  frame: number,
  inAt: number,
  inDur: number,
  outAt: number | null,
  outDur: number,
): number => {
  const pin = ease(frame, inAt, inDur);
  const pout = outAt === null ? 0 : ease(frame, outAt, outDur);
  return (1 - pin) * 108 - pout * 108;
};
