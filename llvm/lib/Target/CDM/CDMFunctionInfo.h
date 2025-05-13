//
// Created by ilya on 20.11.23.
//

#ifndef LLVM_CDMFUNCTIONINFO_H
#define LLVM_CDMFUNCTIONINFO_H

#include "llvm/CodeGen/MachineFrameInfo.h"
#include "llvm/CodeGen/MachineFunction.h"
#include "llvm/CodeGen/MachineMemOperand.h"
#include "llvm/CodeGen/PseudoSourceValue.h"
#include "llvm/CodeGen/Register.h"
#include "llvm/Target/TargetMachine.h"

namespace llvm {

class CDMFunctionInfo : public MachineFunctionInfo {
public:
  CDMFunctionInfo()
      : SRetReturnReg(0), GlobalBaseReg(0), VarArgsFrameIndex(0),
        InArgFIRange(std::make_pair(-1, 0)),
        OutArgFIRange(std::make_pair(-1, 0)), GPFI(0), DynAllocFI(0),
        MaxCallFrameSize(0), EmitNOAT(false) {}
  CDMFunctionInfo(const Function &F, const TargetSubtargetInfo *STI)
      : SRetReturnReg(0), GlobalBaseReg(0), VarArgsFrameIndex(0),
        InArgFIRange(std::make_pair(-1, 0)),
        OutArgFIRange(std::make_pair(-1, 0)), GPFI(0), DynAllocFI(0),
        MaxCallFrameSize(0), EmitNOAT(false) {}

  bool isInArgFI(int FI) const {
    return FI <= OutArgFIRange.first && FI >= OutArgFIRange.second;
  }
  void setLastInArgFI(int FI) { InArgFIRange.second = FI; }

  bool isOutArgFI(int FI) const {
    return FI <= OutArgFIRange.first && FI >= OutArgFIRange.second;
  }

  void extendOutArgFIRange(int FirstFI, int LastFI) {
    if (!OutArgFIRange.second)
      // this must be the first time this function was called.
      OutArgFIRange.first = FirstFI;
    OutArgFIRange.second = LastFI;
  }

  int getGPFI() const { return GPFI; }
  void setGPFI(int FI) { GPFI = FI; }
  bool needGPSaveRestore() const { return getGPFI(); }
  bool isGPFI(int FI) const { return GPFI && GPFI == FI; }

  // The first call to this function creates a frame object for dynamically
  // allocated stack area.
  // int getDynAllocFI() const {
  //   if (!DynAllocFI)
  //     DynAllocFI = MF.getFrameInfo().CreateFixedObject(2, 0, true);

  //   return DynAllocFI;
  // }
  // bool isDynAllocFI(int FI) const { return DynAllocFI && DynAllocFI == FI; }

  unsigned getSRetReturnReg() const { return SRetReturnReg; }
  void setSRetReturnReg(unsigned Reg) { SRetReturnReg = Reg; }

  // bool globalBaseRegFixed() const;
  Register getGlobalBaseReg() const { return GlobalBaseReg; }
  void setGlobalBaseReg(Register Reg) { GlobalBaseReg = Reg; }

  int getVarArgsFrameIndex() const { return VarArgsFrameIndex; }
  void setVarArgsFrameIndex(int Index) { VarArgsFrameIndex = Index; }

  unsigned getMaxCallFrameSize() const { return MaxCallFrameSize; }
  void setMaxCallFrameSize(unsigned S) { MaxCallFrameSize = S; }
  bool getEmitNOAT() const { return EmitNOAT; }
  void setEmitNOAT() { EmitNOAT = true; }

private:
  virtual void anchor();

  unsigned SRetReturnReg;
  Register GlobalBaseReg;
  int VarArgsFrameIndex;
  int RegVarArgFrameindex;
  int VarArgCount = 0;

  std::pair<int, int> InArgFIRange, OutArgFIRange;
  int GPFI;
  mutable int DynAllocFI;
  unsigned MaxCallFrameSize;
  bool EmitNOAT;
};

} // namespace llvm

#endif // LLVM_CDMFUNCTIONINFO_H
