
import { formatDateTime } from "../../utils/formatters";

export interface TimelineItem {
  id: number | string;
  label: string;
  description?: string;
  at?: string;
}

interface ActivityTimelineProps {
  items: TimelineItem[];
}

export function ActivityTimeline({ items }: ActivityTimelineProps) {
  if (!items.length) return <p className="muted">No recent activity</p>;
  return (
    <ul className="activity-timeline">
      {items.map((item) => (
        <li key=item.id}>
          <strong>{item.label}</strong>
          {item.description && <p className="muted">{item.description}</p>}
          {item.at && <time className="muted">{formatDateTime(item.at)}</time>}
        </li>
      ))}
    </ul>
  );
}
