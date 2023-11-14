"""汉字字模（95个ascii+6763个汉字+93个汉字符号）读取示例"""
class HZK:
    def __init__(self,HZKPath,FontPix,useRAM=False):
        """HZKPath字库路径，FontPix字体大小，useRAM是否使用RAM缓存映射数据"""
        self.fhzk=open(HZKPath,"rb")
        #是否使用RAM缓存映射
        self.useRAM=useRAM
        self.sheet={}
        
        if useRAM==True:
            #将映射写入内存，加快读取速度，但RAM会占用27KB左右。
            _buf=self.fhzk.read(6951*4)
            for i in range(6951):
                self.sheet[int.from_bytes(_buf[i*4:i*4+2],"big")]=int.from_bytes(_buf[i*4+2:i*4+4],"big")
        
        #计算单个汉字占用字节
        self.hzSize=int(FontPix*FontPix/8)
        #计算ascii占用字节，这里主要计算入12x12、12x24等比较特殊的字库
        if int(FontPix/2)%8!=0:
            col=(int(FontPix/2)//8)+1 
        else:
            col=int(FontPix/2)//8
        self.ascSize=col*FontPix
    
    def __del__(self):
        self.fhzk.close()
    
    def binarySearch(self, char):
        """二分法查找映射数据"""
        start, end = 0, 6951 - 1 
        while start <= end:
            mid = (start + end) // 2
            self.fhzk.seek(mid * 4)
            buf = self.fhzk.read(4)
            current_char = int.from_bytes(buf[0:2], "big")

            if current_char == ord(char):
                return int.from_bytes(buf[2:4], "big")
            elif current_char < ord(char):
                start = mid + 1
            else:
                end = mid - 1
        return None

    def getCharPos(self, _char):
        """计算指定字符在数据区域的位置"""
        pos = None
        if self.useRAM:
            pos = self.sheet.get(ord(_char))
        else:
            pos = self.binarySearch(_char)
        return pos
                    
    def get(self,_char):
        """获取指定字符的点阵数据"""
        data=b""
        pos=self.getCharPos(_char)
        if pos!=None:
            self.fhzk.seek(pos*self.hzSize+6951*4)
            if ord(_char)<128:
                data=self.fhzk.read(self.ascSize)
            else:
                data=self.fhzk.read(self.hzSize)
        else:
            if ord(_char)<128:
                data=bytes(self.ascSize)
            else:
                data=bytes(self.hzSize)
        return data


"""
#调用示例
_char="测"

#不使用RAM缓存映射数据
hzk=HZK("16x16/HZK16_宋体",16,False)
print(hzk.get(_char))

#使用RAM缓存映射数据（会占用24KB左右的RAM）
hzk1=HZK("16x16/HZK16_宋体",16,True)
print(hzk1.get(_char))
"""
