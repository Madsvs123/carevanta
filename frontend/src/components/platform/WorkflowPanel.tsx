import { useEffect, useState } from "react";
import { PageHeader } from "../layout/PageHeader";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { EmptyState } from "../ui/EmptyState";
import {
  platformActions,
  usePlatformModule,
  type DomainModule,
} from "../../store/platformStore";

type Props = {
  module: DomainModule;
  title: string;
  subtitle?: string;
  defaultOperation?: string;
};

export function WorkflowPanel({ module, title, subtitle, defaultOperation }: Props) {
  const bucket = usePlatformModule(module);
  const [operation, setOperation] = useState(defaultOperation ?? "");
  const [payloadText, setPayloadText] = useState("{\n  \"id\": 1\n}");

  useEffect(() => {
    void platformActions.loadDashboard(module);
  }, [module]);

  useEffect(() => {
    if (!operation && bucket.operations[0]?.name) {
      setOperation(bucket.operations[0].name);
    }
  }, [bucket.operations, operation]);

  async function run() {
    let payload: Record<string, unknown> = {};
    try {
      payload = JSON.parse(payloadText || "{}") as Record<string, unknown>;
    } catch {
      platformActions.clearError(module);
      return;
    }
    await platformActions.runWorkflow(module, operation, payload);
  }

  return (
    <div className="page-section">
      <PageHeader
        title={title}
        subtitle={subtitle ?? "Domain workflows and live dashboard"}
        actions={
          <Button variant="secondary" onClick={() => void platformActions.loadDashboard(module)}>
            Refresh
          </Button>
        }
      />
      {bucket.error ? <p className="error-text">{bucket.error}</p> : null}
      <div className="grid-2">
        <Card title="Dashboard">
          {bucket.loading && !bucket.dashboard ? (
            <p className="muted">Loading…</p>
          ) : bucket.dashboard ? (
            <pre className="code-block">{JSON.stringify(bucket.dashboard, null, 2)}</pre>
          ) : (
            <EmptyState title="No dashboard data" />
          )}
        </Card>
        <Card title="Run operation">
          <label className="field">
            <span>Operation</span>
            <select value={operation} onChange={(e) => setOperation(e.target.value)}>
              {bucket.operations.map((op) => (
                <option key={op.name} value={op.name}>
                  {op.name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Payload (JSON)</span>
            <textarea rows={8} value={payloadText} onChange={(e) => setPayloadText(e.target.value)} />
          </label>
          <Button disabled={bucket.loading || !operation} onClick={() => void run()}>
            {bucket.loading ? "Running…" : "Execute"}
          </Button>
          {bucket.lastResult ? (
            <pre className="code-block" style={{ marginTop: "1rem" }}>
              {JSON.stringify(bucket.lastResult, null, 2)}
            </pre>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
