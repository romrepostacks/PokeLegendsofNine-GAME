// mGBA harness for pilot.py: pilot_harness ROM SAVE, then commands on stdin, one a line:
//   w N            wait N frames, no keys
//   k KEYS N       hold keys N frames (A B E=SELECT S=START U D L R), then release for 4
//   H KEYS N       hold keys N frames, no release
//   G KEYS MAX ADDR LEN   hold keys until the LEN bytes at ADDR change (or MAX frames); prints frames used
//   m ADDR LEN     print LEN bytes at bus address ADDR as hex
//   p FILE.ppm     save the screen
//   M ADDR HEX     write bytes
//   S FILE / L FILE  save / load a savestate (with the save data)
//   c X Y          print the colour at (X, Y)
//   .              print "."
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
static void nolog(struct mLogger* l, int c, enum mLogLevel lv, const char* f, va_list a){}
static uint32_t keys_of(const char* s){ uint32_t k=0; for(;*s;s++){ switch(*s){case 'A':k|=1;break;case 'B':k|=2;break;case 'E':k|=4;break;case 'S':k|=8;break;case 'R':k|=16;break;case 'L':k|=32;break;case 'U':k|=64;break;case 'D':k|=128;break;} } return k; }
int main(int argc, char** argv){
  static struct mLogger lg = { .log = nolog }; mLogSetDefaultLogger(&lg);
  struct mCore* core = mCoreFind(argv[1]); core->init(core); mCoreInitConfig(core, NULL);
  unsigned w,h; core->desiredVideoDimensions(core,&w,&h);
  color_t* buf = malloc(w*h*sizeof(color_t)); core->setVideoBuffer(core, buf, w);
  mCoreLoadFile(core, argv[1]);
  struct VFile* sv = VFileOpen(argv[2], O_RDWR|O_CREAT); core->loadSave(core, sv);
  core->reset(core);
  char line[1024];
  while(fgets(line,sizeof line,stdin)){
    char cmd[8], a[512]; a[0]=0; int n=0;
    if(sscanf(line,"%7s %511s %d",cmd,a,&n)<1) continue;
    if(cmd[0]=='w'){ int f=atoi(a); core->setKeys(core,0); for(int i=0;i<f;i++) core->runFrame(core); }
    else if(cmd[0]=='k'){ core->setKeys(core,keys_of(a)); for(int i=0;i<(n?n:4);i++) core->runFrame(core); core->setKeys(core,0); for(int i=0;i<4;i++) core->runFrame(core); }
    else if(cmd[0]=='H'){ core->setKeys(core,keys_of(a)); for(int i=0;i<n;i++) core->runFrame(core); }
    else if(cmd[0]=='G'){ unsigned mx, addr, len; char ks[64]; sscanf(line,"%*s %63s %u %x %u",ks,&mx,&addr,&len);
      uint8_t before[64]; for(unsigned i=0;i<len;i++) before[i]=core->busRead8(core,addr+i);
      core->setKeys(core,keys_of(ks)); unsigned f=0; int changed=0;
      while(f<mx && !changed){ core->runFrame(core); f++; for(unsigned i=0;i<len;i++) if(core->busRead8(core,addr+i)!=before[i]) changed=1; }
      printf("%u\n",f); fflush(stdout); }
    else if(cmd[0]=='m'){ unsigned addr=strtoul(a,0,16); for(int i=0;i<n;i++) printf("%02x",core->busRead8(core,addr+i)); printf("\n"); fflush(stdout); }
    else if(cmd[0]=='p'){ FILE* f=fopen(a,"wb"); fprintf(f,"P6 %u %u 255\n",w,h);
      for(unsigned i=0;i<w*h;i++){ uint32_t px=buf[i]; unsigned char rgb[3]={px&0xff,(px>>8)&0xff,(px>>16)&0xff}; fwrite(rgb,1,3,f);} fclose(f); printf("p\n"); fflush(stdout); }
    else if(cmd[0]=='M'){ unsigned addr=strtoul(a,0,16); char hx[512]; sscanf(line,"%*s %*s %511s",hx);
      for(int i=0;hx[2*i]&&hx[2*i+1];i++){ unsigned v; sscanf(hx+2*i,"%2x",&v); core->busWrite8(core,addr+i,(uint8_t)v);} }
    else if(cmd[0]=='S'){ struct VFile* vf=VFileOpen(a,O_RDWR|O_CREAT|O_TRUNC); int ok=mCoreSaveStateNamed(core,vf,SAVESTATE_SAVEDATA); vf->close(vf); printf("%d\n",ok); fflush(stdout); }
    else if(cmd[0]=='L'){ struct VFile* vf=VFileOpen(a,O_RDONLY); int ok=vf?mCoreLoadStateNamed(core,vf,SAVESTATE_SAVEDATA):0; if(vf) vf->close(vf); printf("%d\n",ok); fflush(stdout); }
    else if(cmd[0]=='c'){ int x=atoi(a), y=n; uint32_t px=buf[y*w+x]; printf("%u %u %u\n",px&0xff,(px>>8)&0xff,(px>>16)&0xff); fflush(stdout); }
    else if(cmd[0]=='.'){ printf(".\n"); fflush(stdout); }
  }
  core->deinit(core); return 0;
}
