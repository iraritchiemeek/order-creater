import Image from 'next/image';
import { Button } from './catalyst/button';

export interface Result {
    id: number;
    hasRepresentation: { previewUrl: string, contentUrl: string }[];
    title: string;
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
                        <a target="_blank" href={result.hasRepresentation[0].contentUrl}>
                            <div className="relative w-full h-[300px]">
                                <Image
                                    src={result.hasRepresentation[0].previewUrl}
                                    alt={result.title}
                                    fill
                                    className="object-contain object-center bg-slate-100"
                                />
                            </div>
                            <p className="mt-2 text-left text-gray-700">
                                {result.title}
                            </p>
                        </a>
                    )}
                </div>
            ))}
        </div>
    );
};