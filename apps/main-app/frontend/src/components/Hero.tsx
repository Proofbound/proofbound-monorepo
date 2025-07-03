import React from 'react';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ProofboundLogo from './Logo';

const Hero = () => {
  const navigate = useNavigate();

  const goToDemo = () => {
    navigate('/demo');
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center text-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Large Logo at Top */}
        <div className="flex justify-center mb-8">
          <div className="flex flex-col items-center">
            <ProofboundLogo 
              className="w-32 h-32 md:w-40 md:h-40 text-gray-600 mb-6 filter drop-shadow-lg animate-pulse" 
              size={160} 
            />
            <div className="inline-flex items-center space-x-2 glass-card px-6 py-3 animate-fade-in">
              <span className="text-gray-700 font-medium font-sans">AI-Powered Book Generation</span>
            </div>
          </div>
        </div>
        
        <h1 className="hero-title">Have you ever wanted to write a book?</h1>

        <p className="hero-subtitle">
          Proofbound makes it easy to write a 200-page book and publish it online — in minutes!
        </p>

        <p className="hero-description">
          Transform your ideas into professionally formatted books with our AI-powered platform. 
          From concept to publication, we handle the technical details so you can focus on your story.
        </p>
        
        <div className="flex justify-center items-center mb-12 animate-slide-up" style={{animationDelay: '0.8s'}}>
          <button
            onClick={goToDemo}
            className="cta-button space-x-2 transform hover:scale-105 transition-all duration-300 text-xl px-12 py-6"
          >
            <span>Try Our Demo</span>
            <ArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>
    </section>
  );
};

export default Hero;