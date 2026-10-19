import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { createClient } from '../frontend/node_modules/genlayer-js/dist/index.js';
import { studionet } from '../frontend/node_modules/genlayer-js/dist/chains/index.js';

const [address, txHash] = process.argv.slice(2);
if (!/^0x[a-fA-F0-9]{40}$/.test(address || '') || !/^0x[a-fA-F0-9]{64}$/.test(txHash || '')) {
  throw new Error('Usage: node scripts/collect_studionet_proof.mjs <contractAddress> <deploymentTxHash>');
}

const client = createClient({ chain: studionet });
const [localCode, deployedCode, transaction, schema, stats, standards] = await Promise.all([
  readFile(new URL('../contracts/fitted_contract.py', import.meta.url), 'utf8'),
  client.getContractCode(address),
  client.getTransaction({ hash: txHash }),
  client.getContractSchema(address),
  client.readContract({ address, functionName: 'get_stats', args: [] }),
  client.readContract({ address, functionName: 'list_standards', args: [0, 24] }),
]);
const sha256 = value => createHash('sha256').update(value, 'utf8').digest('hex');
const votes = transaction.lastRound ? Object.fromEntries(
  transaction.lastRound.roundValidators.map((validator, index) => [
    validator,
    transaction.lastRound.validatorVotesName[index],
  ]),
) : (transaction.consensus_data?.votes || {});
const proof = {
  collectedAt: new Date().toISOString(),
  network: { name: 'GenLayer StudioNet', chainId: 61999, rpc: studionet.rpcUrls.default.http[0] },
  contractAddress: address,
  deploymentTransaction: {
    hash: txHash,
    status: transaction.statusName,
    result: transaction.resultName,
    executionResult: transaction.txExecutionResultName,
    validatorVotes: votes,
    validatorsTotal: transaction.lastRound?.roundValidators.length,
    validatorsCommitted: transaction.lastRound?.votesCommitted,
    validatorsRevealed: transaction.lastRound?.votesRevealed,
    rounds: transaction.numOfRounds,
  },
  source: {
    localSha256: sha256(localCode),
    deployedSha256: typeof deployedCode === 'string' ? sha256(deployedCode) : null,
    deployedMatchesLocal: typeof deployedCode === 'string' ? sha256(deployedCode) === sha256(localCode) : false,
    genvmVersion: 'v0.2.16',
    genlayerJsVersion: '1.1.8',
    genlayerCliVersion: '0.39.1',
    genlayerTestVersion: '0.29.2',
    genvmLinterVersion: '0.11.0',
  },
  latestFinalizedReads: { schema, stats, standards },
};
console.log(JSON.stringify(proof, (_, value) => typeof value === 'bigint' ? value.toString() : value, 2));
