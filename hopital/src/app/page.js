import { DataTable } from "@/components/data-table";
import { SectionCards } from "@/components/section-cards";
import { ChartBarInteractive } from "@/components/chart-bar-interactive";

async function getPatients() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/patients/all`, {
    cache: "no-store",
  });

  if (!res.ok) return [];

  const data = await res.json();
  return data.patients;
}

export default async function Page() {
  const patients = await getPatients();

  return (
    <div className="flex flex-1 flex-col">
      <div className="@container/main flex flex-1 flex-col gap-2">
        <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">

          <SectionCards patients={patients} />

          <div className="px-4 lg:px-6">
            <ChartBarInteractive patients={patients} />
          </div>

          <DataTable data={patients} />

        </div>
      </div>
    </div>
  );
}