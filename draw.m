u=imread('emma.png');
i=rgb2gray(u);
w=edge(i,'canny',[.05,.20]);

EyeDetect = vision.CascadeObjectDetector('EyePairBig');
if step(EyeDetect,u)
BB=step(EyeDetect,u);
l=round(BB(1,4)/3);
for s=(BB(1,2)+l):(BB(1,2)+2*l)
    for t=BB(1,1):(BB(1,1)+BB(1,3))
        if i(s,t)<72
           w(s,t)=1;
        end
    end
end
end

I=imrotate(w,180);
imshow(w);
impixelinfo;
a=arduino('COM3');
servoAttach(a,9);
servoAttach(a,8);
servoAttach(a,7);
set(0,'RecursionLimit',2000);
servoWrite(a,7,85);
pause(0.02);
global E R;
E=servoRead(a,9);
R=servoRead(a,8);
pause(0.1);
e=size(I);
for p=2:1:e(1,1)
    for t=2:1:e(1,2)
       if I(p,t)==1
           I=draw(a,I,p,t);
       end    
    end
end   
 

