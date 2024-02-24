clear all; close all; clc
a=webcam;
suma=[];

for i = 1:200
    b=snapshot(a);
    c=snapshot(a);
    d=b-c;suma=[suma,sum(d(:))];
    figure(1);imshow(d);
    if sum(d(:)) > 5e6; e=b;
    end
end
figure;plot(suma);
figure;imshow(e);
%imwrite(e,) -> Terminar
%Mostrar solo lo que hay en la silueta