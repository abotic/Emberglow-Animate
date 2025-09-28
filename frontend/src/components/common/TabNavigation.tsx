interface TabNavigationProps {
  activeTab: 'image' | 'video';
  onTabChange: (tab: 'image' | 'video') => void;
}

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  const tabs = [
    { id: 'image' as const, label: 'Generate Image' },
    { id: 'video' as const, label: 'Animate Image' },
  ];

  return (
    <div className="flex justify-center mb-8">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-1 shadow-xl border border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-5 py-2.5 rounded-lg font-medium transition-all duration-300 text-sm md:text-base ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                : 'text-gray-400 hover:bg-gray-700/50 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}