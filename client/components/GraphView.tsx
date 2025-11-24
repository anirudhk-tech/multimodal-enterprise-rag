"use client";

import { useState, useCallback, useEffect } from "react";
import {
  ReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type PokemonNode = {
  name: string;
  generation: number;
  primary_type?: string | null;
  secondary_type?: string | null;
};

type TypeNode = {
  name: string;
};

type GraphResponse = {
  pokemon_nodes: PokemonNode[];
  type_nodes: TypeNode[];
  pokemon_type_edges: { from_pokemon: string; to_type: string }[];
  evolution_edges: { from_pokemon: string; to_pokemon: string }[];
  mentions_edges: { from_media_id: string; to_pokemon: string }[];
};

const API_BASE = "http://localhost:8000"; // adjust if you proxy

export const GraphView = ({
  updateGraphVisual,
}: {
  updateGraphVisual: boolean;
}) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const res = await fetch(`${API_BASE}/graph`);
        if (!res.ok) {
          throw new Error(`Failed to fetch graph: ${res.status}`);
        }
        const graph: GraphResponse = await res.json();

        const builtNodes: Node[] = [];
        const builtEdges: Edge[] = [];

        const centerX = 0;
        const centerY = 0;

        // simple radial layout for pokemon nodes
        const pokemon = graph.pokemon_nodes;
        const radius = 220;
        const angleStep = pokemon.length ? (2 * Math.PI) / pokemon.length : 0;

        pokemon.forEach((p, idx) => {
          const angle = idx * angleStep;
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);

          builtNodes.push({
            id: `pokemon:${p.name}`,
            data: {
              label: p.name,
              generation: p.generation,
            },
            position: { x, y },
            sourcePosition: Position.Right,
            targetPosition: Position.Left,
            style: {
              borderRadius: 999,
              padding: 8,
              background: "#020617",
              border: "1px solid #22c55e",
              color: "#e5e7eb",
              fontSize: 11,
            },
          });
        });

        // type nodes in a column on the right
        graph.type_nodes.forEach((t, idx) => {
          const x = centerX + 360;
          const y = centerY + idx * 90 - graph.type_nodes.length * 45;

          builtNodes.push({
            id: `type:${t.name}`,
            data: { label: t.name },
            position: { x, y },
            sourcePosition: Position.Right,
            targetPosition: Position.Left,
            style: {
              borderRadius: 999,
              padding: 6,
              background: "#020617",
              border: "1px dashed #334155",
              color: "#e5e7eb",
              fontSize: 10,
            },
          });
        });

        // pokemon-type edges
        graph.pokemon_type_edges.forEach((e, idx) => {
          builtEdges.push({
            id: `pt:${idx}:${e.from_pokemon}->${e.to_type}`,
            source: `pokemon:${e.from_pokemon}`,
            target: `type:${e.to_type}`,
            animated: false,
            style: { stroke: "#38bdf8" },
          });
        });

        // evolution edges between pokemon
        graph.evolution_edges.forEach((e, idx) => {
          builtEdges.push({
            id: `evo:${idx}:${e.from_pokemon}->${e.to_pokemon}`,
            source: `pokemon:${e.from_pokemon}`,
            target: `pokemon:${e.to_pokemon}`,
            animated: true,
            style: { stroke: "#22c55e" },
          });
        });

        setNodes(builtNodes);
        setEdges(builtEdges);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchGraph();
  }, [updateGraphVisual]);

  const onNodesChange = useCallback(
    (changes: any) =>
      setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
    [],
  );

  const onEdgesChange = useCallback(
    (changes: any) =>
      setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
    [],
  );

  const onConnect = useCallback(
    (params: any) =>
      setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
    [],
  );

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center text-xs text-slate-400">
        Loading graph...
      </div>
    );
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
    />
  );
};
