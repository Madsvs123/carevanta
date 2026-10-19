import { useCallback, useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom";
import { insuranceApi } from "../../api/insurance";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";

export default function InsuranceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [checks, setChecks] = useState<Record<string, unknown>[]>([]);
  const [auths, setAuths] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [policy, elig, prior] = Promise.all([
        insuranceApi.get(id),
        insuranceApi.listEligibility({ policy: String(id) }).catch(() => ({ results: [] })),
        insuranceApi.listPriorAuths({ policy: String(id) }).catch(() => ({ results: [] })),
      ]);
      setRecord(policy);
      setChecks(elig.results ?? []);
      setAuths(prior.results ?? []);
    } catch {
      setRecord(null);
      toast("Unable to load policy", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  async function run(action: () => Promise<unknown>, ok: string) {
    setBusy(true);
    try {
      await action();
      toast(ok, "success");
      void load();
    } catch {
      toast("Action failed", "error");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <p className="muted">Loading…</p>;
  if (!record) {
    return (
      <EmptyState title="Not found" action={<Button onClick={() => navigate("/insurance")}>Back</Button>} />
    );
  }

  return (
    <div className="detail-workspace">
      <PageHeader
        title={String(record.plan_name || `Policy #${id}`)}
        subtitle={`Member ${String(record.member_id ?? "—")} · ${formatStatus(String(record.coverage_type ?? ""))}`}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/insurance")}>
              Back
            </Button>
            <Button
              disabled={busy || Boolean(record.is_verified)}
              onClick={() => void run(() => insuranceApi.verify(String(id)), "Verified")}
            >
              {record.is_verified ? "Verified" : "Verify policy"}
            </Button>
            <Button
              variant="secondary"
              disabled={busy}
              onClick={() =>
                void run(
                  () => insuranceApi.createEligibility({ policy: Number(id) }),
                  "Eligibility check created",
                )
              }
            >
              New eligibility check
            </Button>
          </>
        }
      />
      <div className="grid-2">
        <Card title="Coverage">
          <dl className="summary-dl">
            <div>
              <dt>Member ID</dt>
              <dd>{String(record.member_id ?? "—")}</dd>
            </div>
            <div>
              <dt>Group</dt>
              <dd>{String(record.group_number ?? "—")}</dd>
            </div>
            <div>
              <dt>Deductible</dt>
              <dd>{String(record.deductible ?? "—")}</dd>
            </div>
            <div>
              <dt>Coinsurance</dt>
              <dd>{String(record.coinsurance_percent ?? "—")}%</dd>
            </div>
            <div>
              <dt>Effective</dt>
              <dd>
                {String(record.effective_from ?? "—")} → {String(record.effective_to ?? "open")}
              </dd>
            </div>
            <div>
              <dt>Verified</dt>
              <dd>
                {record.is_verified
                  ? `Yes ${record.verified_at ? formatDateTime(String(record.verified_at)) : ""}`
                  : "No"}
              </dd>
            </div>
          </dl>
        </Card>
        <Card title="Eligibility checks">
          {checks.length === 0 ? (
            <p className="muted">No checks yet.</p>
          ) : (
            <ul className="plain-list">
              {checks.map((c) => (
                <li key={String(c.id)} className="action-bar">
                  <span>
                    #{String(c.id)} · {formatStatus(String(c.status))}
                    {c.checked_at ? ` · ${formatDateTime(String(c.checked_at))}` : ""}
                  </span>
                  {c.status === "pending" ? (
                    <Button
                      size="sm"
                      disabled={busy}
                      onClick={() => void run(() => insuranceApi.runEligibility(String(c.id)), "Checked")}
                    >
                      Run
                    </Button>
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
      <Card title="Prior authorizations">
        {auths.length === 0 ? (
          <p className="muted">No prior auths for this policy.</p>
        ) : (
          <ul className="plain-list">
            {auths.map((a) => (
              <li key={String(a.id)} className="action-bar">
                <span>
                  {String(a.service_code)} · {String(a.service_description)} ·{" "}
                  {formatStatus(String(a.status))}
                </span>
                <span className="chip-row">
                  {a.status === "draft" ? (
                    <Button
                      size="sm"
                      disabled={busy}
                      onClick={() => void run(() => insuranceApi.submitPriorAuth(String(a.id)), "Submitted")}
                    >
                      Submit
                    </Button>
                  ) : null}
                  {a.status === "submitted" ? (
                    <>
                      <Button
                        size="sm"
                        disabled={busy}
                        onClick={() => void run(() => insuranceApi.approvePriorAuth(String(a.id)), "Approved")}
                      >
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        disabled={busy}
                        onClick={() => void run(() => insuranceApi.denyPriorAuth(String(a.id)), "Denied")}
                      >
                        Deny
                      </Button>
                    </>
                  ) : null}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
