'use client';

import { useEffect, useRef, useCallback } from 'react';
import { TrackLayout } from '@/lib/api';
import { CarPosition, useReplayStore } from '@/lib/store';

interface TrackCanvasProps {
  trackLayout: TrackLayout | null;
  cars: CarPosition[];
}

export default function TrackCanvas({ trackLayout, cars }: TrackCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { selectedDriverId, selectDriver } = useReplayStore();

  // Transform track coordinates to canvas coordinates
  const transformCoords = useCallback((
    x: number[],
    y: number[],
    width: number,
    height: number,
    padding: number = 60
  ) => {
    if (x.length === 0) return { points: [], scale: 1, offsetX: 0, offsetY: 0, minX: 0, minY: 0 };
    
    const minX = Math.min(...x);
    const maxX = Math.max(...x);
    const minY = Math.min(...y);
    const maxY = Math.max(...y);
    
    const trackWidth = maxX - minX;
    const trackHeight = maxY - minY;
    
    const scaleX = (width - padding * 2) / trackWidth;
    const scaleY = (height - padding * 2) / trackHeight;
    const scale = Math.min(scaleX, scaleY);
    
    const offsetX = (width - trackWidth * scale) / 2 - minX * scale;
    const offsetY = (height - trackHeight * scale) / 2 - minY * scale;
    
    const points = x.map((px, i) => ({
      x: px * scale + offsetX,
      y: y[i] * scale + offsetY,
    }));
    
    return { points, scale, offsetX, offsetY, minX, minY };
  }, []);

  // Draw function
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Set canvas size
    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.scale(dpr, dpr);
    
    const width = rect.width;
    const height = rect.height;
    
    // Clear canvas
    ctx.fillStyle = '#15151E';
    ctx.fillRect(0, 0, width, height);
    
    // Draw track if available
    if (trackLayout && trackLayout.x && trackLayout.y) {
      const { points, scale, offsetX, offsetY, minX, minY } = transformCoords(
        trackLayout.x,
        trackLayout.y,
        width,
        height
      );
      
      if (points.length > 0) {
        // Draw track outline
        ctx.strokeStyle = '#38383F';
        ctx.lineWidth = 20;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.closePath();
        ctx.stroke();
        
        // Draw track surface
        ctx.strokeStyle = '#2D2D35';
        ctx.lineWidth = 16;
        ctx.stroke();
        
        // Draw center line
        ctx.strokeStyle = '#1F1F27';
        ctx.lineWidth = 1;
        ctx.setLineDash([10, 10]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      
      // Draw cars
      cars.forEach((car) => {
        const carX = car.x * scale + offsetX;
        const carY = car.y * scale + offsetY;
        
        const isSelected = car.driver_id === selectedDriverId;
        const carSize = isSelected ? 12 : 8;
        
        // Car circle
        ctx.beginPath();
        ctx.arc(carX, carY, carSize, 0, Math.PI * 2);
        ctx.fillStyle = car.team_color || '#808080';
        ctx.fill();
        
        // Border for selected
        if (isSelected) {
          ctx.strokeStyle = '#FFFFFF';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
        
        // Driver code label
        ctx.fillStyle = '#FFFFFF';
        ctx.font = `${isSelected ? 'bold ' : ''}10px sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(car.driver_code || `P${car.position}`, carX, carY - carSize - 4);
        
        // DRS indicator
        if (car.drs_active) {
          ctx.fillStyle = '#22C55E';
          ctx.beginPath();
          ctx.arc(carX + carSize, carY - carSize, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      });
    } else {
      // No track layout - draw placeholder
      ctx.fillStyle = '#38383F';
      ctx.font = '16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Track layout not available', width / 2, height / 2);
      ctx.fillStyle = '#666';
      ctx.font = '12px sans-serif';
      ctx.fillText('Telemetry data required for visualization', width / 2, height / 2 + 24);
    }
  }, [trackLayout, cars, selectedDriverId, transformCoords]);

  // Handle canvas click
  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !trackLayout) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const { scale, offsetX, offsetY } = transformCoords(
      trackLayout.x,
      trackLayout.y,
      rect.width,
      rect.height
    );
    
    // Find clicked car
    for (const car of cars) {
      const carX = car.x * scale + offsetX;
      const carY = car.y * scale + offsetY;
      const dist = Math.sqrt((x - carX) ** 2 + (y - carY) ** 2);
      
      if (dist < 15) {
        selectDriver(car.driver_id === selectedDriverId ? null : car.driver_id);
        return;
      }
    }
    
    // Click on empty space - deselect
    selectDriver(null);
  }, [trackLayout, cars, selectedDriverId, selectDriver, transformCoords]);

  // Redraw on changes
  useEffect(() => {
    draw();
  }, [draw]);

  // Resize handler
  useEffect(() => {
    const handleResize = () => draw();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [draw]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <canvas
        ref={canvasRef}
        onClick={handleClick}
        className="cursor-pointer"
      />
    </div>
  );
}
