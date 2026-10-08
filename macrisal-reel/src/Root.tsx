import React from 'react';
import {Composition} from 'remotion';
import {DURATION_S, FPS, HEIGHT, WIDTH} from './config';
import {Reel} from './Reel';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel}
    durationInFrames={DURATION_S * FPS}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
