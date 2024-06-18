% Genereer low pass filter voor INDPROJ

fs = 44100;

H = [ones(1,1) zeros(1,1000)];
H = [ H fliplr(H) ];
H=H(1:length(H)-1);
h=ifft(H);
h=fftshift(h);
h = h .* hanning(length(h))';

avansfftplot([h zeros(1,1000)], fs);