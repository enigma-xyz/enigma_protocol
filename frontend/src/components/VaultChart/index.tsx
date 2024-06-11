import { format } from "date-fns";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function VaultChart() {
  const [isReady, setIsReady] = useState(false);
  const formatDate = (date: string | Date) => {
    if (isNaN(new Date(date).getTime())) return "";
    return format(new Date(date), "dd/MM");
  };
  useEffect(() => {
    setIsReady(true);
  }, []);
  const data = [
    {
      name: formatDate("2-06-2024"),
      uv: 4000,
      pv: 2400,
      amt: 2400,
    },
    {
      name: formatDate("3-06-2024"),
      uv: 3000,
      pv: 1398,
      amt: 2210,
    },
    {
      name: formatDate("4-06-2024"),
      uv: 2000,
      pv: 9800,
      amt: 2290,
    },
    {
      name: formatDate("5-06-2024"),
      uv: 2780,
      pv: 3908,
      amt: 2000,
    },
    {
      name: formatDate("6-06-2024"),
      uv: 1890,
      pv: 4800,
      amt: 2181,
    },
    {
      name: formatDate("7-06-2024"),
      uv: 2390,
      pv: 3800,
      amt: 2500,
    },
    {
      name: formatDate("8-06-2024"),
      uv: 3490,
      pv: 4300,
      amt: 2100,
    },
  ];
  return (
    <div>
      {isReady && (
        <ResponsiveContainer width={"100%"} height={350}>
          <AreaChart data={data} margin={{ top: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="name" />
            <YAxis dataKey={"amt"} />
            <CartesianGrid strokeDasharray="1 1" />
            <Tooltip />
            <Area
              spacing={4}
              type="monotone"
              dataKey="uv"
              stroke="#8884d8"
              fillOpacity={1}
              fill="url(#colorUv)"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
