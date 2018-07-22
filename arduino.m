function I=draw(a,I,m,n)
if I(m-1,n-1)==1||I(m,n-1)==1||I(m-1,n)==1||I(m+1,n-1)==1||I(m-1,n+1)==1||I(m,n+1)==1||I(m+1,n)==1||I(m+1,n+1)==1
   reach(a,m,n,size(I));
   servoWrite(a,7,92);
    pause(0.01);
   r=size(I);
   I(m,n)=0;
  if m-1>0&&n-1>0&&m<r(1,1)&&n<r(1,2)
      for i=m-1:m+1
          for j=n-1:n+1
              if I(i,j)==1
                 I=draw(a,I,i,j); 
              end
          end
      end
   end
end
  servoWrite(a,7,85);
  pause(0.01);
end

function reach(a,m,n,s)
global E R;
t=calct(m,n,s(1,1),s(1,2));
p=calcp(m,n,s(1,1),s(1,2));
servoAngle(a,9,180-p);
servoAngle(a,8,180-t);
E=180-p;
R=180-t;

end

function t=calct(r,c,o,u)
y=(r/o)*30 + 4;
x=(c/u)*20 + 4;
h=(800-(x*x+y*y))/800;
k=acosd(h);
k=k*10;
t=round(k);
t=t/10;
end

function p=calcp(r,c,o,u)
y=(r/o)*30 + 4;
x=(c/u)*20 + 4;
h=(800-(x*x+y*y))/800;
l=acosd(h);
k=atand(x/y)+(l/2);
k=k*10;
p=round(k);
p=p/10;
end
 
function servoAngle(a,p,n)
global E R;
if p==9
    if abs(E-n)>1
        if n>E
            for i=E:0.1:n
                servoWrite(a,p,i);
               %pause(0.0001);
            end
            pause(0.5);
        else 
             for i=n:0.1:E
                 servoWrite(a,p,E-i+n);
                %pause(0.0001);
             end
             pause(0.5);
        end
    else
        servoWrite(a,p,n);
    end
else
    if abs(R-n)>1
        if n>R
            for i=R:0.1:n
                servoWrite(a,p,i);
                %pause(0.0001);
            end
            pause(0.5);
        else 
             for i=n:0.1:R
                 servoWrite(a,p,R-i+n);
                 %pause(0.0001);
             end
             pause(0.5);
        end
    else
        servoWrite(a,p,n);
    end 
end
end