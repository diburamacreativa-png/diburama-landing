import React from 'react';
import {AbsoluteFill, Audio, Img, staticFile, useCurrentFrame} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {AUDIO, CLOSING, COLORS, FONTS, TIMING, TYPE, sec} from './config';
import {CARDS, DARK_RANGES, NUMBERS, RULES} from './choreography';
import {Card} from './components/Card';
import {Kickers, MaskLine, Rule, Titles} from './components/Type';
import {ease} from './lib/motion';

loadFont({family: FONTS.display, url: staticFile('fonts/Geist-Medium.woff2'), weight: '500'});
loadFont({family: FONTS.display, url: staticFile('fonts/Geist-SemiBold.woff2'), weight: '600'});
loadFont({family: FONTS.mono, url: staticFile('fonts/ibm-plex-mono-latin-400-normal.woff2'), weight: '400'});
loadFont({family: FONTS.mono, url: staticFile('fonts/ibm-plex-mono-latin-500-normal.woff2'), weight: '500'});

// Fondo oscuro: un panel sube desde abajo y sale por arriba.
const DarkPanel: React.FC<{from: number; to: number}> = ({from, to}) => {
  const frame = useCurrentFrame();
  const end = sec(26);
  const top = (1 - ease(frame, sec(from), TIMING.wipe)) * 100;
  const bottom = sec(to) >= end ? 0 : ease(frame, sec(to), TIMING.wipe) * 100;
  if (top >= 100 || bottom >= 100) return null;
  return (
    <AbsoluteFill
      style={{background: COLORS.dark, clipPath: `inset(${top}% 0% ${bottom}% 0%)`}}
    />
  );
};

const BigNumber: React.FC<(typeof NUMBERS)[number]> = ({text, from, to, x, y, align}) => (
  <div
    style={{
      position: 'absolute',
      top: y,
      ...(align === 'left' ? {left: x} : {right: 1080 - x}),
      fontFamily: FONTS.display,
      fontWeight: 600,
      fontSize: 260,
      lineHeight: 1,
      letterSpacing: '-0.065em',
      color: COLORS.accent,
    }}
  >
    <MaskLine inAt={sec(from)} outAt={sec(to)} inDur={12} outDur={TIMING.titleOut}>
      {text}
    </MaskLine>
  </div>
);

const Closing: React.FC = () => {
  const start = sec(24) + 2; // entra en cuanto despejan las ventanas
  return (
    <div style={{position: 'absolute', left: 76, top: 760, width: 960, color: COLORS.light}}>
      {CLOSING.logo ? (
        <MaskLine inAt={start} outAt={null} inDur={14}>
          <Img src={staticFile(CLOSING.logo)} style={{height: 150, display: 'block'}} />
        </MaskLine>
      ) : (
        <MaskLine inAt={start} outAt={null} inDur={14}>
          <div
            style={{
              fontFamily: FONTS.display,
              fontWeight: 600,
              fontSize: TYPE.closingBrandSize,
              lineHeight: 1,
              letterSpacing: '-0.06em',
            }}
          >
            {CLOSING.brand}
          </div>
        </MaskLine>
      )}
      <div style={{height: 44}} />
      <div
        style={{
          fontFamily: FONTS.display,
          fontWeight: 500,
          fontSize: TYPE.closingTaglineSize,
          lineHeight: 1.04,
          letterSpacing: '-0.035em',
        }}
      >
        {wrapTagline(CLOSING.tagline).map((line, i) => (
          <MaskLine key={i} inAt={start + 4 + i * TIMING.lineStagger} outAt={null} inDur={12}>
            {line}
          </MaskLine>
        ))}
      </div>
    </div>
  );
};

// Divide la frase final en dos líneas equilibradas.
const wrapTagline = (t: string): string[] => {
  const words = t.split(' ');
  if (words.length < 3) return [t];
  let best = 1;
  let bestDiff = Infinity;
  for (let i = 1; i < words.length; i++) {
    const d = Math.abs(words.slice(0, i).join(' ').length - words.slice(i).join(' ').length);
    if (d < bestDiff) {
      bestDiff = d;
      best = i;
    }
  }
  return [words.slice(0, best).join(' '), words.slice(best).join(' ')];
};

export const Reel: React.FC = () => {
  return (
    <AbsoluteFill style={{background: COLORS.light}}>
      {DARK_RANGES.map(([a, b]) => (
        <DarkPanel key={a} from={a} to={b} />
      ))}
      {RULES.map((r, i) => (
        <Rule key={i} x={r.x} y={r.y} w={r.w} h={r.h} inAt={sec(r.from)} outAt={r.to === null ? null : sec(r.to)} />
      ))}
      {NUMBERS.map((n) => (
        <BigNumber key={n.text} {...n} />
      ))}
      {CARDS.map((c) => (
        <Card key={c.id} spec={c} />
      ))}
      <Kickers />
      <Titles />
      <Closing />
      {AUDIO.soundtrack ? <Audio src={staticFile(AUDIO.soundtrack)} volume={AUDIO.volume} /> : null}
    </AbsoluteFill>
  );
};
