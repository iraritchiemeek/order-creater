import Image from 'next/image';

interface Result {
    id: number;
    hasRepresentation: { previewUrl: string, title: string }[];
}

interface ResultsProps {
    results: Result[];
}

export const Results = ({ results }: ResultsProps) => {
    return (
        <div className="w-full grid grid-cols-3 gap-x-4 gap-y-8">
            {results.map((result, index) => (
                <div key={index} className="relative w-full flex flex-col">
                    {result.hasRepresentation.length > 0 && (
                        <a href={`https://collections.tepapa.govt.nz/object/${result.id}`}>
                            <div className="relative w-full h-[300px]">
                                <Image
                                    src={result.hasRepresentation[0].previewUrl}
                                    alt={result.hasRepresentation[0].title.split(';').slice(1).join('\n')}
                                    fill
                                    className="object-contain object-left"
                                />
                            </div>
                            <p className="mt-2 text-left text-gray-700">
                                {result.hasRepresentation[0].title.split(';').slice(1).map((line, idx) => (
                                    <span key={idx}>{line}<br /></span>
                                ))}
                            </p>
                        </a>
                    )}
                </div>
            ))}
        </div>
    );
};