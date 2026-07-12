export const meta = {
  name: 'review-branch',
  description: 'Review changed files in parallel and return one ranked, deduplicated report',
}

const base = args?.base ?? 'main'

const discovered = await agent(
  `List source, test, configuration, and migration files changed relative to ${base}. Exclude generated files and lock files unless their content is directly relevant.`,
  {
    label: 'discover-changed-files',
    schema: {
      type: 'object',
      required: ['files'],
      properties: {
        files: { type: 'array', items: { type: 'string' } },
      },
    },
  },
)

const reviews = await pipeline(discovered.files, file =>
  agent(
    `Review ${file} and its relevant diff for correctness, architecture, security, privacy, idempotency, logging, tests, and backward compatibility. Return only evidence-backed findings with severity and remediation.`,
    { label: file },
  ),
)

return await agent(
  `Synthesize these per-file reviews into one ranked report. Deduplicate findings, discard unsupported claims, identify cross-file risks, and explicitly state when no material issue remains:\n${JSON.stringify(reviews)}`,
  { label: 'synthesize-review' },
)
