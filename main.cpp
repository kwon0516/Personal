#include <iostream>

int main()
{
    for (int i = 0; i != 10; i++)
    {
        std::cout << i << std::endl;
    }
    
    return 0;
}

if (bSite)
   {
      strInspectPath.Format(_T("\\\\192.168.100.17\\VP_Image\\%s\\%s\\Main\\"), strFolder/*strYear, strMonth, strDay*/, strCellID);
   }
   else
   {
      CString strNasIP;
      if (m_nSelectLine == 1)
         strNasIP = _T("192.168.100.100");
      else
         strNasIP = _T("192.168.100.200");

      strInspectPath.Format(_T("\\\\%s\\nas_storage\\VP_Image\\%s\\%s\\Main\\"), strNasIP, strFolder/*strYear, strMonth, strDay*/, strCellID);
   }

   CreateFolder(strInspectPath);