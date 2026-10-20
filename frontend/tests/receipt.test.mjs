import test from 'node:test';
import assert from 'node:assert/strict';
import { isSuccessfulFinalizedExecution, receiptExecutionLabel, receiptStatusLabel } from '../receipt.js';

test('accepts the SDK normalized successful finalized result', () => {
  assert.equal(isSuccessfulFinalizedExecution({txExecutionResultName:'FINISHED_WITH_RETURN'}), true);
  assert.equal(isSuccessfulFinalizedExecution({txExecutionResultName:'FINISHED_WITH_ERROR'}), false);
});

test('accepts raw StudioNet receipt only with finalized majority and successful VM execution', () => {
  const receipt = {
    status_name: 'FINALIZED',
    result_name: 'MAJORITY_AGREE',
    consensus_data: {leader_receipt:[
      {mode:'leader',execution_result:'SUCCESS',genvm_result:{error_code:null}},
      {mode:'validator',execution_result:'SUCCESS',genvm_result:{error_code:null}},
    ]},
  };
  assert.equal(isSuccessfulFinalizedExecution(receipt), true);
  assert.equal(receiptStatusLabel(receipt), 'FINALIZED');
  assert.equal(receiptExecutionLabel(receipt), 'SUCCESS');
});

test('rejects raw failed, incomplete, or non-majority finalized receipts', () => {
  const base = {status_name:'FINALIZED',result_name:'MAJORITY_AGREE',consensus_data:{leader_receipt:[{mode:'leader',execution_result:'SUCCESS',genvm_result:{error_code:null}}]}};
  assert.equal(isSuccessfulFinalizedExecution({...base,consensus_data:{leader_receipt:[{mode:'leader',execution_result:'FAILURE',genvm_result:{error_code:'execution_error'}}]}}), false);
  assert.equal(isSuccessfulFinalizedExecution({...base,result_name:'MAJORITY_DISAGREE'}), false);
  assert.equal(isSuccessfulFinalizedExecution({status_name:'PENDING',result_name:'MAJORITY_AGREE',consensus_data:base.consensus_data}), false);
  assert.equal(isSuccessfulFinalizedExecution({status_name:'FINALIZED',result_name:'MAJORITY_AGREE'}), false);
});
