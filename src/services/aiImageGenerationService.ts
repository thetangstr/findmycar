/**
 * AI Image Generation Service
 * 
 * This service provides AI-generated car images as a last resort when other methods fail.
 * It uses the Stability AI API to generate realistic car images based on vehicle descriptions.
 */

import { Vehicle } from '@/types';

// API key for Stability AI (should be set in environment variables)
const STABILITY_API_KEY = process.env.NEXT_PUBLIC_STABILITY_API_KEY || '';

// Base URL for Stability AI API
const STABILITY_API_URL = 'https://api.stability.ai/v1/generation';

/**
 * Generates a detailed prompt for the AI model based on vehicle details
 */
const generateDetailedPrompt = (vehicle: Vehicle): string => {
  const { make, model, year, exteriorColor, bodyStyle } = vehicle;
  
  // Build color description
  const colorDesc = exteriorColor && exteriorColor.toLowerCase() !== 'unknown' 
    ? exteriorColor 
    : 'factory color';
    
  // Build body style description
  const bodyDesc = bodyStyle || getDefaultBodyStyle(make, model);
  
  // Build year description
  const yearDesc = year ? `${year}` : 'modern';
  
  // Create the base prompt
  let prompt = `Professional high-quality photograph of a ${yearDesc} ${make} ${model}`;
  
  // Add color information if available
  if (colorDesc !== 'factory color') {
    prompt += ` in ${colorDesc}`;
  }
  
  // Add body style if available
  if (bodyDesc) {
    prompt += `, ${bodyDesc}`;
  }
  
  // Add photographic style guidance
  prompt += `. Professional automotive photography, realistic, detailed, studio lighting, 4k, high resolution`;
  
  return prompt;
};

/**
 * Helper to determine the default body style based on make/model
 */
const getDefaultBodyStyle = (make: string, model: string): string => {
  const searchText = `${make} ${model}`.toLowerCase();
  
  if (searchText.includes('911') || 
      searchText.includes('corvette') || 
      searchText.includes('ferrari') || 
      searchText.includes('lamborghini')) {
    return 'sports car';
  }
  
  if (searchText.includes('f-150') || 
      searchText.includes('silverado') || 
      searchText.includes('ram') || 
      searchText.includes('tacoma')) {
    return 'pickup truck';
  }
  
  if (searchText.includes('rav4') || 
      searchText.includes('cr-v') || 
      searchText.includes('explorer') || 
      searchText.includes('highlander')) {
    return 'SUV';
  }
  
  if (searchText.includes('camry') || 
      searchText.includes('accord') || 
      searchText.includes('civic') || 
      searchText.includes('corolla')) {
    return 'sedan';
  }
  
  return '';
};

/**
 * Generate AI images using Stability AI
 */
export const generateVehicleImages = async (vehicle: Vehicle, count: number = 1): Promise<string[]> => {
  if (!STABILITY_API_KEY) {
    console.warn('Stability AI API key not configured, skipping AI image generation');
    return [];
  }
  
  try {
    // Generate the prompt
    const prompt = generateDetailedPrompt(vehicle);
    console.log(`Generating AI image with prompt: "${prompt}"`);
    
    // Configure the request
    const response = await fetch(`${STABILITY_API_URL}/text-to-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${STABILITY_API_KEY}`
      },
      body: JSON.stringify({
        text_prompts: [
          {
            text: prompt,
            weight: 1
          },
          {
            text: "cartoon, illustration, anime, drawing, low quality, blurry, distorted proportions",
            weight: -1
          }
        ],
        cfg_scale: 7,
        height: 768,
        width: 1024,
        samples: count,
        steps: 30
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Stability AI API error: ${JSON.stringify(error)}`);
    }
    
    const data = await response.json();
    
    // Extract image data from response
    const images = data.artifacts.map((artifact: any) => {
      // Convert base64 to URL or store as base64 data URL
      const base64Data = artifact.base64;
      return `data:image/png;base64,${base64Data}`;
    });
    
    console.log(`Successfully generated ${images.length} AI images for ${vehicle.make} ${vehicle.model}`);
    return images;
  } catch (error) {
    console.error('Error generating AI images:', error);
    return [];
  }
};

/**
 * Utility function to check if the system has a Stability API key configured
 */
export const isAiImageGenerationAvailable = (): boolean => {
  return !!STABILITY_API_KEY;
};

export default {
  generateVehicleImages,
  isAiImageGenerationAvailable
};
