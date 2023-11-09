import React, { useState, useEffect, useRef } from 'react';
import '../styles/Car.css';

function Car() {

  const ww = window.innerWidth;

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [keysDown, setKeysDown] = useState({left: false, right: false});
  const [image, setImage] = useState(new Image());
  const [position, setPosition] = useState({ x: 0, y: 0 }); // Starting position

  useEffect(() => {
    image.src = 'https://placehold.co/500x300'; // Set the image source
    image.onload = () => drawImage(); // Draw the image once it's loaded
    // set startin pos to center
    setPosition({ x: ww/2 - image.width/2, y: 0 })
  }, [image]);

  const drawImage = () => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    ctx.drawImage(image, position.x, position.y); // Draw the image at the new position
  };

  // This effect sets up the keydown event listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        setKeysDown(prev => ({ ...prev, right: true }));
      } else if (e.key === 'ArrowLeft') {
        setKeysDown(prev => ({ ...prev, left: true }));
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        setKeysDown(prev => ({ ...prev, right: false }));
      }
      if (e.key === 'ArrowLeft') {
        setKeysDown(prev => ({ ...prev, left: false }));
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // Redraw the image whenever the position changes
  useEffect(() => {
    drawImage();
  }, [position]);

  // This effect handles the animation
  useEffect(() => {
    let animationFrameId: number;

    // This function will be called every frame
    const animate = () => {

      if (keysDown.right && keysDown.left) {
        return
      }

      // If the right arrow key is pressed, move the image to the right
      if (keysDown.right) {
        setPosition(prev => ({ x: prev.x + 10, y: prev.y }));
      } else if (keysDown.left) {
        setPosition(prev => ({ x: prev.x - 10, y: prev.y }));
      }

      // Request another frame
      animationFrameId = window.requestAnimationFrame(animate);
    };

    // Start the animation
    animationFrameId = window.requestAnimationFrame(animate);

    // This will clean up the animation every time the component is unmounted
    return () => window.cancelAnimationFrame(animationFrameId);
  }, [keysDown]);


  return (
    <canvas ref={canvasRef} className='car-container' width={ww} height={300} />
  );
}

export default Car;
