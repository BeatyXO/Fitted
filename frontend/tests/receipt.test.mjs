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

test('accepts the production StudioNet receipt with SUCCESS and quorum-cancelled validators', () => {
  const receipt = {
    statusName:'FINALIZED',
    result_name:'MAJORITY_AGREE',
    consensus_data:{
      leader_receipt:[
        {mode:'leader',execution_result:'SUCCESS',genvm_result:{error_code:null}},
        {mode:'validator',execution_result:'ERROR',genvm_result:{error_code:'CONSENSUS_VALIDATOR_QUORUM_REACHED'}},
      ],
      validators:[
        {mode:'validator',execution_result:'SUCCESS',genvm_result:{error_code:null}},
        {mode:'validator',execution_result:'ERROR',genvm_result:{error_code:'CONSENSUS_VALIDATOR_QUORUM_REACHED'}},
      ],
    },
  };
  assert.equal(isSuccessfulFinalizedExecution(receipt), true);
  assert.equal(receiptExecutionLabel(receipt), 'SUCCESS');
});

test('falls back to finalized raw StudioNet evidence for unrecognized normalized result names', () => {
  const receipt = {
    txExecutionResultName:'SUCCESS',
    statusName:'FINALIZED',
    result_name:'MAJORITY_AGREE',
    consensus_data:{leader_receipt:[{mode:'leader',execution_result:'SUCCESS',genvm_result:{error_code:null}}]},
  };
  assert.equal(isSuccessfulFinalizedExecution(receipt), true);
});

test('rejects raw failed, incomplete, or non-majority finalized receipts', () => {
  const base = {status_name:'FINALIZED',result_name:'MAJORITY_AGREE',consensus_data:{leader_receipt:[{mode:'leader',execution_result:'SUCCESS',genvm_result:{error_code:null}}]}};
  assert.equal(isSuccessfulFinalizedExecution({...base,consensus_data:{leader_receipt:[{mode:'leader',execution_result:'FAILURE',genvm_result:{error_code:'execution_error'}}]}}), false);
  assert.equal(isSuccessfulFinalizedExecution({...base,consensus_data:{leader_receipt:[{mode:'leader',execution_result:'ERROR',genvm_result:{error_code:'execution_error'}}]}}), false);
  assert.equal(isSuccessfulFinalizedExecution({...base,result_name:'MAJORITY_DISAGREE'}), false);
  assert.equal(isSuccessfulFinalizedExecution({status_name:'PENDING',result_name:'MAJORITY_AGREE',consensus_data:base.consensus_data}), false);
  assert.equal(isSuccessfulFinalizedExecution({status_name:'FINALIZED',result_name:'MAJORITY_AGREE'}), false);
});
