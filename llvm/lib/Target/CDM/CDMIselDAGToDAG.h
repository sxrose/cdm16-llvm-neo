//
// Created by ilya on 21.10.23.
//

#ifndef LLVM_CDMISELDAGTODAG_H
#define LLVM_CDMISELDAGTODAG_H

#include <map>
#include "CDMTargetMachine.h"
#include "CDMInstrInfo.h"

#include "llvm/CodeGen/SelectionDAGISel.h"

namespace llvm {
class CDMDagToDagIsel : public SelectionDAGISel {
public:
  explicit CDMDagToDagIsel(CDMTargetMachine &TM,
                           CodeGenOptLevel OL = CodeGenOptLevel::Default)
      : SelectionDAGISel(TM, OL) {}

  bool runOnMachineFunction(MachineFunction &MF) override;

private:
#include "CDMGenDAGISel.inc"

  std::map<ISD::CondCode, CDMCOND::CondOp> CondMap = {
      {ISD::CondCode::SETLT, CDMCOND::LT},
      {ISD::CondCode::SETLE, CDMCOND::LE},
      {ISD::CondCode::SETGT, CDMCOND::GT},
      {ISD::CondCode::SETGE, CDMCOND::GE},
      {ISD::CondCode::SETULT, CDMCOND::LO},
      {ISD::CondCode::SETULE, CDMCOND::LS},
      {ISD::CondCode::SETUGT, CDMCOND::HI},
      {ISD::CondCode::SETUGE, CDMCOND::HS},
      {ISD::CondCode::SETEQ, CDMCOND::EQ},
      {ISD::CondCode::SETNE, CDMCOND::NE},
  };

  void Select(SDNode *N) override;
  bool trySelect(SDNode *Node);
  bool SelectAddrFrameIndex(SDNode *Parent, SDValue Addr, SDValue &Base,
                            SDValue &Offset);
  bool SelectAddr(SDNode *Parent, SDValue Addr, SDValue &Base, SDValue &Offset);
  bool SelectAddrRR(SDValue Addr, SDValue &Base, SDValue &Offset);

  bool trySelectPointerCall(SDNode *N);
  bool SelectConditionalBranch(SDNode *N);

  bool isImm6(SDValue& V);
  const APInt& getSDValueAsAPInt(SDValue& V); 

  CDMCOND::CondOp CCToCondOp(ISD::CondCode CC) const {
    if (!CondMap.count(CC)) {
      llvm_unreachable("Unknown branch condition");
    }
    return CondMap.at(CC);
  }
};

class CDMDagToDagIselLegacy : public SelectionDAGISelLegacy {
public:
  static char ID;

  StringRef getPassName() const override;

  explicit CDMDagToDagIselLegacy(CDMTargetMachine &TM, CodeGenOptLevel OptLevel)
      : SelectionDAGISelLegacy(
            ID, std::make_unique<CDMDagToDagIsel>(TM, OptLevel)) {}
};

FunctionPass *createCDMISelDagLegacy(CDMTargetMachine &TM,
                                     CodeGenOptLevel OptLevel);

} // namespace llvm

#endif // LLVM_CDMISELDAGTODAG_H
