/**
 * GenLayer 1.1.8 may return normalized execution fields on some RPC paths and
 * the raw finalized receipt on others. Only accept the raw shape when both
 * final consensus and every reported VM execution explicitly succeeded.
 */
export function isSuccessfulFinalizedExecution(receipt, expectedSuccess = 'FINISHED_WITH_RETURN') {
  if (receipt?.txExecutionResultName != null) {
    return receipt.txExecutionResultName === expectedSuccess;
  }

  const status = receipt?.statusName ?? receipt?.status_name;
  const consensus = receipt?.resultName ?? receipt?.result_name;
  const executions = receipt?.consensus_data?.leader_receipt;
  if (status !== 'FINALIZED' || consensus !== 'MAJORITY_AGREE' || !Array.isArray(executions) || executions.length === 0) {
    return false;
  }

  const leader = executions.find(entry => entry?.mode === 'leader');
  return Boolean(leader && executions.every(entry =>
    entry?.execution_result === 'SUCCESS' && !entry?.genvm_result?.error_code
  ));
}

export function receiptStatusLabel(receipt) {
  return receipt?.statusName ?? receipt?.status_name ?? 'unknown';
}

export function receiptExecutionLabel(receipt) {
  if (receipt?.txExecutionResultName != null) return receipt.txExecutionResultName;
  const executions = receipt?.consensus_data?.leader_receipt;
  const leader = Array.isArray(executions) ? executions.find(entry => entry?.mode === 'leader') : null;
  return leader?.execution_result ?? receipt?.execution_result ?? 'unknown';
}
